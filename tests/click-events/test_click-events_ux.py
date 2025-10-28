from __future__ import annotations

import time
import pytest
import allure
from selenium.webdriver.support import expected_conditions as EC

from pages.click_events import ClickEventsPage

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("UX")
@allure.title("[UX-1] Кнопки видимы/активны; #demo обновляется ≤ 500мс")
def test_buttons_are_clickable_and_demo_updates_fast(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    for animal in ("cat", "dog", "pig", "cow"):
        expected = page.expected_message(animal)
        with allure.step(f"{animal.title()}: проверка кликабельности и скорости реакции"):
            assert page.is_button_displayed_and_enabled(animal), f"Кнопка {animal} не кликабельна"

            start = time.monotonic()
            page.click_button(animal)
            page.wait.until(
                EC.text_to_be_present_in_element(page.DEMO_OUTPUT, expected)
            )
            dur_ms = (time.monotonic() - start) * 1000
            allure.attach(f"{dur_ms:.1f} ms", f"latency_{animal}", allure.attachment_type.TEXT)
            assert dur_ms <= 500, f"{animal}: сообщение появилось слишком долго ({dur_ms:.1f} ms > 500 ms)"

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("UX")
@allure.title("[UX-2] Последний клик побеждает (без накопления)")
def test_last_click_wins_no_concatenation(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    page.click_sequence(["cat", "dog", "pig", "cow"])
    final_text = page.get_message()
    assert final_text == page.expected_message("cow"), f"Итог должен быть Moo!, а не {final_text!r}"
    assert "\n" not in final_text and "<" not in final_text, f"Подозрительный контент в #demo: {final_text!r}"
