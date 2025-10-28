from __future__ import annotations
import pytest
import allure
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.popups_page import PopupsPage

@pytest.mark.regression
@allure.feature("Popups")
@allure.story("UX")
class TestPopupsUX:

    def _latency_to_alert(self, page: PopupsPage, trigger, timeout: float = 0.8) -> float:
        t0 = time.monotonic()
        trigger()
        WebDriverWait(page.driver, timeout).until(EC.alert_is_present())
        dt = time.monotonic() - t0
        page.driver.switch_to.alert.accept()
        return dt

    @allure.title("[UX] Кнопки кликабельны, алерты появляются быстро")
    def test_buttons_clickable_and_fast_alert(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        lat_alert = self._latency_to_alert(page, lambda: page.click(page.ALERT_BTN))
        lat_confirm = self._latency_to_alert(page, lambda: page.click(page.CONFIRM_BTN))

        # Prompt: проверяем факт появления
        t0 = time.monotonic()
        page.click(page.PROMPT_BTN)
        WebDriverWait(driver, 0.8).until(EC.alert_is_present())
        driver.switch_to.alert.dismiss()
        lat_prompt = time.monotonic() - t0

        cap = (driver.capabilities or {})
        is_firefox = "firefox" in str(cap.get("browserName", "")).lower()
        limit = 0.8 if is_firefox else 0.5

        for name, lat in (("alert", lat_alert), ("confirm", lat_confirm), ("prompt", lat_prompt)):
            allure.attach(f"{lat:.3f}s", f"{name}_latency", allure.attachment_type.TEXT)
            assert lat < limit, f"{name} алерт появился слишком медленно: {lat:.3f}s (limit={limit:.1f}s)"

    @allure.title("[UX] Tooltip показывается и имеет текст")
    def test_tooltip_visible_and_has_text(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        page.show_tooltip()
        # подождём явной видимости
        ok = WebDriverWait(driver, 1.5).until(lambda d: page.is_tooltip_visible())
        assert ok, "Tooltip не стал видимым"

        tt = page.get_tooltip_text()
        assert tt != ""
