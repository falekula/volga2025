# pages/click_events.py
from __future__ import annotations

import allure
from typing import Dict, Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage, Locator

class ClickEventsPage(BasePage):
    DEMO_OUTPUT: Locator = (By.CSS_SELECTOR, "#demo")

    _BTN_XPATH_BY_TEXT: Dict[str, Locator] = {
        "cat": (By.XPATH, "//button[normalize-space()='Cat']"),
        "dog": (By.XPATH, "//button[normalize-space()='Dog']"),
        "pig": (By.XPATH, "//button[normalize-space()='Pig']"),
        "cow": (By.XPATH, "//button[normalize-space()='Cow']"),
    }

    _BTN_CSS_FALLBACK: Dict[str, Locator] = {
        "cat": (By.CSS_SELECTOR, "div.wp-block-columns:nth-child(3) > div:nth-child(1) > "
                                 "div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > button:nth-child(1)"),
        "dog": (By.CSS_SELECTOR, "div.wp-block-columns:nth-child(3) > div:nth-child(1) > "
                                 "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > button:nth-child(1)"),
        "pig": (By.CSS_SELECTOR, "div.wp-block-columns:nth-child(5) > div:nth-child(1) > button:nth-child(1)"),
        "cow": (By.CSS_SELECTOR, "div.wp-block-columns:nth-child(5) > div:nth-child(2) > button:nth-child(1)"),
    }

    EXPECTED_MESSAGES: Dict[str, str] = {
        "cat": "Meow!",
        "dog": "Woof!",
        "pig": "Oink!",
        "cow": "Moo!",
    }

    @allure.step("Открыть Click Events и дождаться готовности")
    def open_and_ready(self, base_url: str) -> None:
        self.open(f"{base_url.rstrip('/')}/click-events/")
        self.find(self.DEMO_OUTPUT)
        self.find(self._button_locator("cat"))

    @allure.step("Проверить, что открыта страница Click Events")
    def is_open(self, base_url: Optional[str] = None) -> bool:
        try:
            self.find(self.DEMO_OUTPUT)
        except Exception:
            return False
        if base_url:
            cur = self.driver.current_url.rstrip("/").lower()
            need = (base_url.rstrip("/") + "/click-events").lower()
            if not cur.startswith(need):
                return False
        return True

    @allure.step("Клик по кнопке: {name}")
    def click_button(self, name: str) -> None:
        key = name.strip().lower()
        loc = self._button_locator(key)
        el = self.find(loc)
        self._scroll_into_view(el)
        try:
            self.wait_clickable(loc).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    @allure.step("Серия кликов (без пауз) по: {names}")
    def click_sequence(self, names: list[str]) -> None:
        for n in names:
            self.click_button(n)

    @allure.step("Дождаться текста в #demo: {expected!r}")
    def wait_message(self, expected: str, timeout: Optional[int] = None) -> str:
        to = timeout or self.wait._timeout  
        locator = self.DEMO_OUTPUT
        self.wait.with_timeout(to).until(EC.text_to_be_present_in_element(locator, expected))
        return self.get_message()

    @allure.step("Прочитать текст из #demo")
    def get_message(self) -> str:
        return (self.find(self.DEMO_OUTPUT).text or "").strip()

    @allure.step("Проверить, что кнопка отображается и активна: {name}")
    def is_button_displayed_and_enabled(self, name: str) -> bool:
        el = self.find(self._button_locator(name))
        return el.is_displayed() and el.is_enabled()

    @allure.step("Получить видимые тексты всех кнопок")
    def get_all_button_texts(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for key in ("cat", "dog", "pig", "cow"):
            try:
                txt = (self.find(self._button_locator(key)).text or "").strip()
            except Exception:
                txt = ""
            out[key] = txt
        return out

    @allure.step("Проверить live-region у #demo (role/aria-live)")
    def get_live_region_attrs(self) -> Tuple[str, str]:
        el = self.find(self.DEMO_OUTPUT)
        role = (el.get_attribute("role") or "").strip().lower()
        aria_live = (el.get_attribute("aria-live") or "").strip().lower()
        return role, aria_live

    def _button_locator(self, key: str) -> Locator:
        k = key.strip().lower()
        if k in self._BTN_XPATH_BY_TEXT:
            return self._BTN_XPATH_BY_TEXT[k]
        if k in self._BTN_CSS_FALLBACK:
            return self._BTN_CSS_FALLBACK[k]
        raise ValueError(f"Unknown button name: {key!r}")

    @allure.step("Получить ожидаемое сообщение для кнопки: {name}")
    def expected_message(self, name: str) -> str:
        key = name.strip().lower()
        if key not in self.EXPECTED_MESSAGES:
            raise ValueError(f"No expected message for {name!r}")
        return self.EXPECTED_MESSAGES[key]
