from __future__ import annotations

from typing import Tuple, Any
import allure

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

from utils.logger import Logger

Locator = Tuple[By, str]

class BasePage:
    def __init__(self, driver: WebDriver, wait_timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout, poll_frequency=0.2)
        self.log = Logger.get_logger(self.__class__.__name__)

    def open(self, url: str) -> None:
        self.log.info(f"Opening URL: {url}")
        try:
            self.driver.get(url)
        except TimeoutException:
            self.log.warning(f"Page load timed out for {url}; continue with explicit waits")

    def find(self, locator: Locator):
        self.log.debug(f"Find: {locator}")
        return self.wait.until(EC.presence_of_element_located(locator))

    def finds(self, locator: Locator):
        self.log.debug(f"Find all: {locator}")
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def wait_visible(self, locator: Locator):
        self.log.debug(f"Wait visible: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator: Locator):
        self.log.debug(f"Wait clickable: {locator}")
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_invisible(self, locator: Locator, timeout: int | None = None) -> bool:
        self.log.debug(f"Wait invisible: {locator}")
        try:
            WebDriverWait(self.driver, timeout or self.wait._timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def click(self, locator: Locator) -> None:
        self.log.debug(f"Click: {locator}")
        try:
            el = self.wait_clickable(locator)
            self._scroll_into_view(el)
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.log.debug(f"JS click fallback for: {locator}")
            el = self.find(locator)
            self._scroll_into_view(el)
            self.driver.execute_script("arguments[0].click();", el)

    def type(self, locator: Locator, text: str, clear: bool = True) -> None:
        self.log.debug(f"Type into {locator}: '{text}'")
        el = self.wait_visible(locator)
        if clear:
            try:
                el.clear()
            except Exception:
                el.send_keys("\uE009" + "a")
                el.send_keys("\uE003")
        el.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        el = self.wait_visible(locator)
        value = el.text
        self.log.debug(f"Text from {locator}: '{value}'")
        return value

    def is_visible(self, locator: Locator, timeout: int | None = None) -> bool:
        self.log.debug(f"Is visible? {locator}")
        try:
            WebDriverWait(self.driver, timeout or self.wait._timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def exists(self, locator: Locator, timeout: int | None = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def js(self, script: str, *args: Any):
        self.log.debug(f"Execute JS: {script[:60]}...")
        return self.driver.execute_script(script, *args)

    def _scroll_into_view(self, el) -> None:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        except Exception:
            pass

    def screenshot_png(self) -> bytes:
        self.log.info("Taking screenshot")
        return self.driver.get_screenshot_as_png()

    @allure.step("Ожидать появления JS-алерта (timeout={timeout}s)")
    def wait_for_alert(self, timeout: int = 5):
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(EC.alert_is_present())
            return self.driver.switch_to.alert
        except TimeoutException:
            return None

    @allure.step("Принять (accept) алерт, если он есть")
    def accept_alert_if_present(self, timeout: int = 5) -> str | None:
        alert = self.wait_for_alert(timeout)
        if not alert:
            return None
        text = ""
        try:
            text = alert.text or ""
            allure.attach(text, "alert_text", allure.attachment_type.TEXT)
        except Exception:
            pass
        try:
            alert.accept()
        except Exception:
            pass
        return text

    @allure.step("Закрыть (dismiss) алерт, если он есть")
    def dismiss_alert_if_present(self, timeout: int = 5) -> str | None:
        alert = self.wait_for_alert(timeout)
        if not alert:
            return None
        text = ""
        try:
            text = alert.text or ""
            allure.attach(text, "alert_text", allure.attachment_type.TEXT)
        except Exception:
            pass
        try:
            alert.dismiss()
        except Exception:
            pass
        return text
