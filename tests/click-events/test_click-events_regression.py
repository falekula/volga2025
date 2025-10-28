from __future__ import annotations

import pytest
import allure

from pages.click_events import ClickEventsPage

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("Regression")
@allure.title("[REG-1] Идемпотентность: повторные клики не ломают состояние")
def test_idempotent_repeated_clicks(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    for i in range(3):
        with allure.step(f"Клик #{i+1} по Cat"):
            page.click_button("cat")
            assert page.get_message() == page.EXPECTED_MESSAGES["cat"]
            assert "/click-events" in driver.current_url

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("Regression")
@allure.title("[REG-2] Порядок важен: последовательные клики стабильно дают последний текст")
def test_ordered_clicks_yield_last_message(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    for animal in ("cat", "pig", "dog"):
        expected = page.expected_message(animal)
        with allure.step(f"{animal.title()}: ждём {expected!r}"):
            page.click_button(animal)
            assert page.get_message() == expected
