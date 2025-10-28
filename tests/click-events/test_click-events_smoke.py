from __future__ import annotations

import pytest
import allure

from pages.click_events import ClickEventsPage

@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("Smoke")
@allure.title("[SMOKE] Клик по каждой кнопке даёт правильный текст в #demo")
def test_buttons_show_expected_messages(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    for animal in ("cat", "dog", "pig", "cow"):
        expected = page.expected_message(animal)
        with allure.step(f"Клик по {animal.title()} → ожидаем {expected!r}"):
            page.click_button(animal)
            actual = page.get_message()
            assert actual == expected, f"{animal}: ожидали {expected!r}, получили {actual!r}"
            assert "/click-events" in driver.current_url
