from __future__ import annotations
import pytest
import allure
from selenium.webdriver.common.keys import Keys

from pages.popups_page import PopupsPage

@pytest.mark.regression
@allure.feature("Popups")
@allure.story("Accessibility")
class TestPopupsA11y:

    @allure.title("[A11y] Space/Enter активируют кнопки (Alert/Confirm/Prompt) без мыши")
    def test_keyboard_activation(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        btn = page.find(page.ALERT_BTN)
        driver.execute_script("arguments[0].focus();", btn)
        btn.send_keys(Keys.SPACE)
        driver.switch_to.alert.accept()

        btn = page.find(page.CONFIRM_BTN)
        driver.execute_script("arguments[0].focus();", btn)
        btn.send_keys(Keys.ENTER)
        driver.switch_to.alert.accept()

        btn = page.find(page.PROMPT_BTN)
        driver.execute_script("arguments[0].focus();", btn)
        btn.send_keys(Keys.ENTER)
        driver.switch_to.alert.dismiss()

    @allure.title("[A11y] Tooltip: role=tooltip и aria-describedby (мягко/xfail)")
    def test_tooltip_has_role_and_describedby(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)
        ok = page.tooltip_accessibility_ok()
        if not ok:
            pytest.xfail("На стенде tooltip не помечен role=tooltip/aria-describedby — известное ограничение")
