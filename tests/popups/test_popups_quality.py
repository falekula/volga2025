from __future__ import annotations
import pytest
import allure
import time

from pages.popups_page import PopupsPage

@pytest.mark.chrome_only
@pytest.mark.regression
@allure.feature("Popups")
@allure.story("Quality")
@allure.severity(allure.severity_level.CRITICAL)
def test_no_severe_console_errors_on_interactions(driver, base_url, wait_timeout):
    name = (driver.capabilities or {}).get("browserName", "").lower()
    assert "chrome" in name, "Этот тест рассчитан на Chrome/Chromium (browser logs)"

    NOISY = ("deprecated_endpoint", "favicon", "manifest", "gcm", "chrome-extension",
             "swiftshader", "webgl", "ERR_BLOCKED_BY_CLIENT", "ERR_CONNECTION_REFUSED")

    def browser_severe():
        entries = driver.get_log("browser") or []
        return [e for e in entries
                if str(e.get("level", "")).upper() == "SEVERE"
                and not any(n in str(e.get("message", "")).lower() for n in NOISY)]

    page = PopupsPage(driver, wait_timeout)
    page.open_and_ready(base_url)

    try:
        driver.get_log("browser")
    except Exception:
        pass

    page.click_alert_and_accept()
    page.click_confirm_and_choose(accept=True)
    page.click_confirm_and_choose(accept=False)
    page.click_prompt_and_respond("QualityCheck", accept=True)

    severe = browser_severe()
    if severe:
        allure.attach("\n".join(str(x) for x in severe), "severe", allure.attachment_type.TEXT)
    assert not severe
