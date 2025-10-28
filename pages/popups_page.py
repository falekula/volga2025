from __future__ import annotations

import time
import allure
from typing import Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage, Locator


class PopupsPage(BasePage):
    """POM: practice-automation.com/popups/"""

    # --- Локаторы ---
    ALERT_BTN: Locator = (By.CSS_SELECTOR, "#alert")
    CONFIRM_BTN: Locator = (By.CSS_SELECTOR, "#confirm")
    PROMPT_BTN: Locator = (By.CSS_SELECTOR, "#prompt")

    CONFIRM_RESULT: Locator = (By.CSS_SELECTOR, "#confirmResult")
    PROMPT_RESULT: Locator = (By.CSS_SELECTOR, "#promptResult")

    TOOLTIP_BTN: Locator = (By.CSS_SELECTOR, ".tooltip_1")
    TOOLTIP: Locator = (By.CSS_SELECTOR, "#myTooltip")

    # --- Навигация/готовность ---
    @allure.step("Открыть Popups и дождаться кнопок")
    def open_and_ready(self, base_url: str) -> None:
        self.open(f"{base_url.rstrip('/')}/popups/")
        self.find(self.ALERT_BTN)
        self.find(self.CONFIRM_BTN)
        self.find(self.PROMPT_BTN)

    @allure.step("Проверить, что открыта страница Popups")
    def is_open(self, base_url: str | None = None) -> bool:
        try:
            self.find(self.ALERT_BTN)
            self.find(self.CONFIRM_BTN)
            self.find(self.PROMPT_BTN)
        except Exception:
            return False
        if base_url:
            cur = self.driver.current_url.rstrip("/").lower()
            expected = f"{base_url.rstrip('/').lower()}/popups"
            if not cur.startswith(expected):
                return False
        return True

    # --- Действия с алертами ---
    def _wait_alert(self, timeout: float = 3.0) -> Optional[Alert]:
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            return self.driver.switch_to.alert
        except Exception:
            return None

    @allure.step("Alert: кликнуть и принять")
    def click_alert_and_accept(self, timeout: float = 3.0) -> Optional[str]:
        self.click(self.ALERT_BTN)
        al = self._wait_alert(timeout)
        if not al:
            return None
        text = al.text
        al.accept()
        return text

    @allure.step("Confirm: кликнуть и выбрать accept={accept}")
    def click_confirm_and_choose(self, accept: bool = True, timeout: float = 3.0) -> Tuple[Optional[str], str]:
        self.click(self.CONFIRM_BTN)
        al = self._wait_alert(timeout)
        alert_text = None
        if al:
            alert_text = al.text
            if accept:
                al.accept()
            else:
                al.dismiss()
        txt = self.wait_text_any(self.CONFIRM_RESULT, timeout=timeout) or self.get_confirm_result()
        return alert_text, txt

    @allure.step("Prompt: кликнуть, ввести текст и accept={accept}")
    def click_prompt_and_respond(self, text: str = "", accept: bool = True, timeout: float = 3.0) -> Tuple[Optional[str], str]:
        """
        Стандартно работаем с нативным prompt; если драйвер/браузер капризничает,
        у нас всё равно будет результат на странице — это главное для автотестов.
        """
        self.click(self.PROMPT_BTN)
        alert_text = None
        al = self._wait_alert(timeout)

        if al:
            # Нативный prompt появился — пробуем штатно
            alert_text = al.text
            try:
                if accept:
                    try:
                        al.send_keys(text)
                    except Exception:
                        # мелкая задержка иногда помогает в FF
                        time.sleep(0.05)
                        al.send_keys(text)
                    al.accept()
                else:
                    al.dismiss()
            except Exception:
                # fallback: всё равно закрыть, чтобы страница не зависла
                try:
                    al.dismiss()
                except Exception:
                    pass
        else:
            # На некоторых стендах prompt может быть переопределён — просто ждём результат
            pass

        txt = self.wait_text_any(self.PROMPT_RESULT, timeout=timeout) or self.get_prompt_result()
        return alert_text, txt

    # --- Результаты на странице ---
    @allure.step("Прочитать текст #confirmResult")
    def get_confirm_result(self) -> str:
        return (self.find(self.CONFIRM_RESULT).text or "").strip()

    @allure.step("Прочитать текст #promptResult")
    def get_prompt_result(self) -> str:
        return (self.find(self.PROMPT_RESULT).text or "").strip()

    # --- Tooltip ---
    @allure.step("Показать tooltip кликом по кнопке и подождать видимость")
    def show_tooltip(self, timeout: float = 1.5) -> None:
        self.click(self.TOOLTIP_BTN)
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: self.is_tooltip_visible())
        except Exception:
            pass

    @allure.step("Tooltip видим?")
    def is_tooltip_visible(self) -> bool:
        try:
            el = self.find(self.TOOLTIP)
        except Exception:
            return False
        try:
            visible = self.js("""
                const el = arguments[0];
                const s = window.getComputedStyle(el);
                const vis = s.visibility !== 'hidden';
                const disp = s.display !== 'none';
                const op = parseFloat(s.opacity) > 0.01;
                const box = el.getBoundingClientRect();
                return !!(vis && disp && op && box.width >= 1 && box.height >= 1);
            """, el)
            return bool(visible)
        except Exception:
            return el.is_displayed()

    @allure.step("Прочитать текст tooltip (#myTooltip)")
    def get_tooltip_text(self) -> str:
        try:
            return (self.find(self.TOOLTIP).text or "").strip()
        except Exception:
            return ""

    def _wait_confirm_result(self, expected: str, timeout: float = 3.0) -> str:
        expected = (expected or "").strip()
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: (self.get_confirm_result() or "").strip() == expected
            )
        except TimeoutException:
            pass
        return (self.get_confirm_result() or "").strip()

    def click_confirm_and_choose(self, accept: bool = True) -> tuple[str, str]:
        """Надёжно кликает Confirm и возвращает (action, text)."""
        # текущее значение нам не важно — ждём именно ожидаемое после клика
        self.click(self.CONFIRM_BTN)
        alert = WebDriverWait(self.driver, 2.5).until(EC.alert_is_present())
        expected = "OK it is!" if accept else "Cancel it is!"
        (alert.accept if accept else alert.dismiss)()

        txt = self._wait_confirm_result(expected, timeout=3.0)

        # Если вдруг не совпало — микро-ретрай (редкий флейк в Chrome)
        if txt != expected:
            # повторно вызовем confirm с тем же действием
            self.click(self.CONFIRM_BTN)
            alert = WebDriverWait(self.driver, 2.5).until(EC.alert_is_present())
            (alert.accept if accept else alert.dismiss)()
            txt = self._wait_confirm_result(expected, timeout=3.0)

        return ("accept" if accept else "dismiss"), txt
    
    def button_accessible_name(self, locator: Locator) -> str:
        el = self.find(locator)
        name = self.js("""
            const el = arguments[0];
            const aria = el.getAttribute('aria-label');
            if (aria) return aria.trim();
            const txt = (el.textContent||'').trim();
            return txt;
        """, el) or ""
        return name.strip()

    def tooltip_accessibility_ok(self) -> bool:
        """True, если #myTooltip имеет role=tooltip и привязан через aria-describedby."""
        try:
            btn = self.find(self.TOOLTIP_BTN)
            t = self.find(self.TOOLTIP)
        except Exception:
            return False
        role = (t.get_attribute("role") or "").strip().lower()
        desc = (btn.get_attribute("aria-describedby") or "").strip()
        tid = (t.get_attribute("id") or "").strip()
        return (role == "tooltip") and (tid and desc and tid in desc)

    def wait_text_any(self, locator: Locator, timeout: float = 2.0) -> str:
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: (d.find_element(*locator).text or "").strip() != "")
            return (self.find(locator).text or "").strip()
        except Exception:
            return ""
