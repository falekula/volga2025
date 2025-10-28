from __future__ import annotations

import pytest
import allure
from selenium.webdriver.common.keys import Keys

from pages.click_events import ClickEventsPage

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("Accessibility")
@allure.title("[A11y-1] Клавиатурная доступность: Space/Enter активируют кнопки")
def test_keyboard_activation_updates_demo(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    with allure.step("Focus на Cat → SPACE → Meow!"):
        cat_btn = page.find(page._button_locator("cat"))  
        cat_btn.send_keys(Keys.SPACE)
        assert page.get_message() == page.EXPECTED_MESSAGES["cat"]

    with allure.step("Focus на Dog → ENTER → Woof!"):
        dog_btn = page.find(page._button_locator("dog"))
        dog_btn.send_keys(Keys.ENTER)
        assert page.get_message() == page.EXPECTED_MESSAGES["dog"]

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("Accessibility")
@allure.title("[A11y-2] Live-region у #demo (мягкая проверка с xfail)")
def test_live_region_or_known_limitation(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    role, aria_live = page.get_live_region_attrs()
    has_live = (role == "status") or (aria_live in {"polite", "assertive"})
    if not has_live:
        pytest.xfail("На стенде #demo не помечен как live-region (aria-live/role=status) — известное ограничение")

    page.click_button("pig")
    assert page.get_message() == page.EXPECTED_MESSAGES["pig"]
