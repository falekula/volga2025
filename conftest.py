from __future__ import annotations

import os
import json
import pytest
import allure

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from utils.logger import Logger

log = Logger.get_logger("conftest")

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox", "both"],
        help="Browser for tests: chrome, firefox, or both",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browsers in headless mode",
    )
    parser.addoption(
        "--base-url",
        action="store",
        default="https://practice-automation.com",
        help="Base URL of AUT",
    )
    parser.addoption(
        "--window-width",
        action="store",
        default="1920",
        help="Browser window width (used in headless too)",
    )
    parser.addoption(
        "--window-height",
        action="store",
        default="1080",
        help="Browser window height (used in headless too)",
    )
    parser.addoption(
        "--wait-timeout",
        action="store",
        default="10",
        help="Default explicit wait timeout (seconds)",
    )

def pytest_generate_tests(metafunc):
    if "driver" not in metafunc.fixturenames:
        return
    
    chrome_only = bool(list(metafunc.definition.iter_markers(name="chrome_only")))
    firefox_only = bool(list(metafunc.definition.iter_markers(name="firefox_only")))

    if chrome_only and firefox_only:
        raise pytest.UsageError("Test cannot be both @chrome_only and @firefox_only")

    if chrome_only:
        params = ["chrome"]
    elif firefox_only:
        params = ["firefox"]
    else:
        browser_opt = metafunc.config.getoption("--browser")
        params = ["chrome", "firefox"] if browser_opt == "both" else [browser_opt]

    metafunc.parametrize("driver", params, indirect=True, ids=[f"browser={b}" for b in params])

def _build_chrome(headless: bool, w: int, h: int) -> webdriver.Chrome:
    options = ChromeOptions()
    options.page_load_strategy = "eager"

    options.add_argument(f"--window-size={w},{h}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--high-dpi-support=1")
    options.add_argument("--disable-features=Translate,AutomationControlled")

    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if headless:
        options.add_argument("--headless=new")

    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    if remote_url:
        log.info(f"Using remote Chrome at {remote_url}")
        driver = webdriver.Remote(command_executor=remote_url, options=options)
        driver.set_window_size(w, h)
        return driver

    return webdriver.Chrome(options=options)

def _build_firefox(headless: bool, w: int, h: int) -> webdriver.Firefox:
    options = FirefoxOptions()
    options.page_load_strategy = "eager"
    if headless:
        options.add_argument("-headless")

    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    if remote_url:
        log.info(f"Using remote Firefox at {remote_url}")
        driver = webdriver.Remote(command_executor=remote_url, options=options)
        driver.set_window_size(w, h)
        return driver

    driver = webdriver.Firefox(options=options)
    driver.set_window_size(w, h)
    return driver

def get_driver(browser_name: str, headless: bool, w: int, h: int) -> webdriver.Remote:
    if browser_name == "chrome":
        return _build_chrome(headless, w, h)
    if browser_name == "firefox":
        return _build_firefox(headless, w, h)
    raise ValueError(f"Unsupported browser: {browser_name}")

def pytest_generate_tests(metafunc):
    if "driver" in metafunc.fixturenames:
        browser = metafunc.config.getoption("--browser")
        params = ["chrome", "firefox"] if browser == "both" else [browser]
        metafunc.parametrize("driver", params, indirect=True, ids=params)

@pytest.fixture(scope="session")
def base_url(request) -> str:
    return request.config.getoption("--base-url").rstrip("/")

@pytest.fixture(scope="session")
def wait_timeout(request) -> int:
    return int(request.config.getoption("--wait-timeout"))

@pytest.fixture(scope="session", autouse=True)
def _allure_env(request, base_url):
    try:
        os.makedirs("allure-results", exist_ok=True)
        env = {
            "base_url": base_url,
            "browser": request.config.getoption("--browser"),
            "headless": str(bool(request.config.getoption("--headless") or os.getenv("CI"))),
            "window": f"{request.config.getoption('--window-width')}x{request.config.getoption('--window-height')}",
            "remote": os.getenv("SELENIUM_REMOTE_URL") or "",
        }
        with open(os.path.join("allure-results", "environment.properties"), "w", encoding="utf-8") as f:
            for k, v in env.items():
                f.write(f"{k}={v}\n")
    except Exception:
        pass


@pytest.fixture
def driver(request) -> webdriver.Remote:
    browser_name = request.param
    headless = bool(request.config.getoption("--headless") or os.getenv("CI"))
    w = int(request.config.getoption("--window-width"))
    h = int(request.config.getoption("--window-height"))
    node = request.node
    chrome_only = node.get_closest_marker("chrome_only") is not None
    firefox_only = node.get_closest_marker("firefox_only") is not None
    if chrome_only and browser_name != "chrome":
        pytest.skip("chrome_only: пропускаем запуск не в Chrome/Chromium")
    if firefox_only and browser_name != "firefox":
        pytest.skip("firefox_only: пропускаем запуск не в Firefox")

    log.info(f"Initializing {browser_name} (headless={headless}) {w}x{h}")
    drv = get_driver(browser_name, headless, w, h)

    drv.set_page_load_timeout(60)
    drv.set_script_timeout(30)
    drv.implicitly_wait(0)

    yield drv

    log.info(f"Closing {browser_name}")
    try:
        drv.quit()
    except Exception as e:
        log.exception(f"Error on driver.quit(): {e}")

def _attach_artifacts_if_possible(driver: webdriver.Remote) -> None:
    # Скриншот
    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, "screenshot", allure.attachment_type.PNG)
    except Exception:
        pass

    try:
        html = driver.page_source
        allure.attach(html, "page_source.html", allure.attachment_type.HTML)
    except Exception:
        pass

    try:
        url = driver.current_url
        allure.attach(url, "current_url.txt", allure.attachment_type.TEXT)
    except Exception:
        pass

    try:
        caps = driver.capabilities or {}
        allure.attach(json.dumps(caps, indent=2, ensure_ascii=False), "capabilities.json", allure.attachment_type.JSON)
    except Exception:
        pass

    try:
        name = (driver.capabilities or {}).get("browserName", "").lower()
        if "chrome" in name or "chromium" in name:
            logs = driver.get_log("browser") or []
            if logs:
                text = "\n".join(str(x) for x in logs)
                allure.attach(text, "browser_console.txt", allure.attachment_type.TEXT)
    except Exception:
        pass

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.failed and rep.when in ("setup", "call"):
        driver = item.funcargs.get("driver")
        if not driver:
            return
        _attach_artifacts_if_possible(driver)
