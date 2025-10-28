from __future__ import annotations

import pytest
import allure
from selenium.webdriver.common.by import By

from pages.click_events import ClickEventsPage

def _get_h1_text(driver) -> str:
    candidates = [
        (By.CSS_SELECTOR, "h1.entry-title"),
        (By.CSS_SELECTOR, "article h1"),
        (By.CSS_SELECTOR, ".pt-1 h1"),
        (By.XPATH, "//main//h1[normalize-space()]"),
        (By.XPATH, "//h1[normalize-space()]"),
    ]
    for by, sel in candidates:
        try:
            el = driver.find_element(by, sel)
            t = (el.text or "").strip()
            if t:
                return t
        except Exception:
            continue
    return ""

@pytest.mark.regression
@allure.feature("Click Events")
@allure.story("Content")
@allure.title("[CONTENT] Копирайтинг: заголовок, лейблы кнопок и точные тексты #demo")
def test_content_labels_and_messages(driver, base_url, wait_timeout):
    page = ClickEventsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    with allure.step("Проверить H1 содержит 'Click' (мягко)"):
        h1 = _get_h1_text(driver)
        assert h1, "На странице нет H1"
        assert "click" in h1.lower(), f"Ожидали 'Click' в H1, получили: {h1!r}"

    with allure.step("Проверить видимые тексты кнопок"):
        texts = page.get_all_button_texts()
        assert texts["cat"] == "Cat"
        assert texts["dog"] == "Dog"
        assert texts["pig"] == "Pig"
        assert texts["cow"] == "Cow"

    with allure.step("Клик по каждой кнопке даёт точную строку с пунктуацией"):
        for animal, expected in page.EXPECTED_MESSAGES.items():
            page.click_button(animal)
            assert page.get_message() == expected
