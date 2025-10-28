from __future__ import annotations

import re
import allure
from typing import Dict, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.base_page import BasePage, Locator

class FormPage(BasePage):
    NAME_INPUT: Locator = (By.CSS_SELECTOR, "#name-input")
    PASSWORD_INPUT_PRIMARY: Locator = (By.CSS_SELECTOR, "#feedbackForm > label:nth-child(3) > input:nth-child(1)")
    PASSWORD_INPUT_FALLBACK: Locator = (By.CSS_SELECTOR, "input[type='password']")
    EMAIL_INPUT: Locator = (By.CSS_SELECTOR, "#email")
    MESSAGE_TEXTAREA: Locator = (By.CSS_SELECTOR, "#message")
    SUBMIT_BTN: Locator = (By.CSS_SELECTOR, "#submit-btn")
    H1_FORM_FIELDS: Locator = (By.CSS_SELECTOR, ".pt-1 > h1:nth-child(1)")
    AUTOMATION_SELECT: Locator = (By.CSS_SELECTOR, "#automation")

    _DRINK_IDS: Dict[str, str] = {
        "water": "#drink1",
        "milk": "#drink2",
        "coffee": "#drink3",
        "wine": "#drink4",
        "ctrl-alt-delight": "#drink5",
    }

    _COLOR_IDS: Dict[str, str] = {
        "red": "#color1",
        "blue": "#color2",
        "green": "#color3",
        "#ffc0cb": "#color4",
    }

    _KNOWN_TOOLS: List[str] = ["selenium", "playwright", "cypress", "appium", "katalon studio"]

    @allure.step("Открыть Form Fields и дождаться готовности")
    def open_and_ready(self, base_url: str) -> None:
        self.open(f"{base_url}/form-fields/")
        from selenium.webdriver.common.by import By
        self.find((By.TAG_NAME, "body"))
        self.find(self.NAME_INPUT)

    @allure.step("Проверить, что открыта страница Form Fields")
    def is_open(self, base_url: str | None = None) -> bool:
        try:
            self.find(self.NAME_INPUT)
        except TimeoutException:
            return False

        if base_url:
            cur = self.driver.current_url.rstrip("/").lower()
            expected_prefix = (base_url.rstrip("/") + "/form-fields").lower()
            if not cur.startswith(expected_prefix):
                return False

        h1 = (self.get_h1_text() or "").strip().lower()
        if h1 and "form fields" not in h1:
            pass

        return True

    @allure.step("Безопасно кликнуть по label[for='{control_id}']")
    def click_label_for(self, control_id: str) -> None:
        from selenium.webdriver.common.by import By
        css = f"label[for='{control_id}']"
        lbl = self.driver.find_element(By.CSS_SELECTOR, css)
        self._scroll_into_view(lbl)
        try:
            self.wait_clickable((By.CSS_SELECTOR, css)).click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", lbl)

    @allure.step("Получить 'доступное имя' или ближайший контекстный текст")
    def get_accessible_name_or_context(self, el) -> str:
        return self.js(r"""
            const el = arguments[0];

            const norm = s => (s||'').replace(/\s+/g,' ').trim().toLowerCase();
            const getText = n => norm(n ? n.textContent : '');

            const lbls = el.labels ? Array.from(el.labels).map(x => getText(x)).filter(Boolean) : [];
            if (lbls.length) return lbls.join(' ').trim();

            const ariaLabelledby = el.getAttribute('aria-labelledby');
            if (ariaLabelledby) {
            const parts = ariaLabelledby.split(/\s+/).map(id => document.getElementById(id)).filter(Boolean);
            const txt = parts.map(n => getText(n)).filter(Boolean).join(' ').trim();
            if (txt) return txt;
            }

            const aria = norm(el.getAttribute('aria-label'));
            if (aria) return aria;

           let p = el.previousElementSibling, hops = 0;
            while (p && hops < 3) { const t = getText(p); if (t) return t; p = p.previousElementSibling; hops++; }

            const cont = el.closest('article .entry-content, form, main, body') || document.body;
            const rect = el.getBoundingClientRect();
            const nodes = Array.from(cont.querySelectorAll('label, p, span, div, h1, h2, h3'));
            let best = '', bestDy = Infinity;
            for (const n of nodes) {
            const txt = getText(n); if (!txt) continue;
            const r = n.getBoundingClientRect(); const dy = rect.top - r.bottom;
            if (dy >= 0 && dy < bestDy) { bestDy = dy; best = txt; }
            }
            return best;
        """, el) or ""


    @allure.step("Fill Name: {text}")
    def fill_name(self, text: str) -> None:
        self.type(self.NAME_INPUT, text)

    @allure.step("Fill Password: ••••")
    def fill_password(self, text: str) -> None:
        locator = self._resolve_password_locator()
        self.type(locator, text)

    @allure.step("Fill Email: {text}")
    def fill_email(self, text: str) -> None:
        self.type(self.EMAIL_INPUT, text)

    @allure.step("Fill Message")
    def fill_message(self, text: str) -> None:
        self.type(self.MESSAGE_TEXTAREA, text)

    @allure.step("Select favorite drink: {option}")
    def select_drink(self, option: str) -> None:
        css = self._by_dict_safe(self._DRINK_IDS, option)
        self.click((By.CSS_SELECTOR, css))

    @allure.step("Select favorite color: {option}")
    def select_color(self, option: str) -> None:
        css = self._by_dict_safe(self._COLOR_IDS, option)
        self.click((By.CSS_SELECTOR, css))

    @allure.step("Set 'Do you like automation?': {value}")
    def select_automation_preference(self, value: str) -> None:
        value_norm = self._norm(value)
        sel = Select(self.find(self.AUTOMATION_SELECT))
        allowed = {"yes", "no", "undecided", "default"}
        if value_norm in allowed:
            try:
                sel.select_by_value(value_norm)
            except Exception:
                try:
                    sel.select_by_visible_text(value)
                except Exception:
                    sel.select_by_index(0)
        else:
            sel.select_by_visible_text(value)

    @allure.step("Toggle automation tool: {tool_name}")
    def toggle_tool(self, tool_name: str, check: bool = True) -> None:
        tool_norm = self._norm(tool_name)
        root = self._find_tools_container()

        label = self._find_label_by_text(root, tool_norm)
        if label:
            for_id = label.get_attribute("for")
            if for_id:
                cb = root.find_element(By.ID, for_id)
                self._set_checkbox(cb, check)
                return
            before = self._label_checked_state(label)
            label.click()
            after = self._label_checked_state(label)
            if (check and not after) or ((not check) and after):
                try:
                    inner = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    self._set_checkbox(inner, check)
                except Exception:
                    pass
            return

        try:
            xpath = (
                ".//input[@type='checkbox' and "
                "(following-sibling::*[contains(translate(normalize-space(.), "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), "
                f"'{tool_norm}')] or "
                "preceding-sibling::*[contains(translate(normalize-space(.), "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), "
                f"'{tool_norm}')])]"
            )
            cb = root.find_element(By.XPATH, xpath)
            self._set_checkbox(cb, check)
            return
        except Exception:
            pass

        raise NoSuchElementException(f"Checkbox for tool '{tool_name}' not found")

    @allure.step("Collect list of Automation tools from the page")
    def get_all_tools(self) -> List[str]:
        root = self._find_tools_container()
        texts: List[str] = []

        for el in root.find_elements(By.XPATH, ".//label"):
            t = self._clean_text(el.text)
            if t:
                texts.append(t)

        for el in root.find_elements(By.XPATH, ".//li|.//p|.//span|.//div"):
            t = self._clean_text(el.text)
            if t:
                texts.append(t)

        seen = set()
        result: List[str] = []
        for t in texts:
            lt = self._norm(t)
            if lt in seen:
                continue
            if lt in self._KNOWN_TOOLS:
                result.append(t.strip())
                seen.add(lt)
        return result

    @allure.step("Submit form")
    def submit(self) -> None:
        self.click(self.SUBMIT_BTN)

    def visible_warnings(self) -> List[str]:
        lower = "translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"
        elems = self.driver.find_elements(
            By.XPATH,
            f"//*[self::div or self::p or self::span][@role='alert' or "
            f"contains({lower},'warning') or contains({lower},'error') or "
            "contains(translate(normalize-space(text()),"
            " 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'warning')]"
        )
        return [e.text.strip() for e in elems if e.is_displayed() and e.text.strip()]

    @allure.step("Получить текст главного заголовка (H1) страницы")
    def get_h1_text(self) -> str:
        candidates: list[Locator] = [
            (By.CSS_SELECTOR, "h1.entry-title"),
            (By.CSS_SELECTOR, "article h1"),
            (By.CSS_SELECTOR, ".pt-1 h1"),
            (By.XPATH, "//main//h1[normalize-space()]"),
            (By.XPATH, "//h1[normalize-space()]"),
        ]
        for by, sel in candidates:
            try:
                el = self.driver.find_element(by, sel)
                txt = (el.text or "").strip()
                if txt:
                    return txt
            except Exception:
                continue
        return ""

    def _resolve_password_locator(self) -> Locator:
        try:
            self.find(self.PASSWORD_INPUT_PRIMARY)
            return self.PASSWORD_INPUT_PRIMARY
        except Exception:
            return self.PASSWORD_INPUT_FALLBACK

    def _by_dict_safe(self, mapping: Dict[str, str], key: str) -> str:
        k = self._norm(key)
        if k not in mapping:
            raise ValueError(f"Unsupported option '{key}'. Allowed: {', '.join(mapping.keys())}")
        return mapping[k]

    def _find_tools_container(self):
        d = self.driver
        candidates = d.find_elements(
            By.XPATH,
            "//*[self::h2 or self::h3 or self::p]"
            "[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
            " 'automation tools')]"
        )
        if candidates:
            h = candidates[0]
            try:
                return h.find_element(By.XPATH, "./ancestor::*[contains(@class,'entry-content')][1]")
            except Exception:
                return h
        try:
            return d.find_element(By.CSS_SELECTOR, "article .entry-content")
        except Exception:
            return d.find_element(By.TAG_NAME, "body")

    def _find_label_by_text(self, root, tool_norm: str):
        xpath = (
            ".//label[translate(normalize-space(.),"
            " 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')="
            f"'{tool_norm}']"
        )
        els = root.find_elements(By.XPATH, xpath)
        return els[0] if els else None

    def _label_checked_state(self, label_el) -> bool:
        try:
            cb = label_el.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            return bool(cb.is_selected())
        except Exception:
            return False

    def _set_checkbox(self, cb, check: bool) -> None:
        if (check and not cb.is_selected()) or ((not check) and cb.is_selected()):
            self._scroll_into_view(cb)
            cb.click()

    @staticmethod
    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip().lower())

    @staticmethod
    def _clean_text(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip())