from __future__ import annotations
import re
import pytest
import allure
from pages.popups_page import PopupsPage

@pytest.mark.regression
@allure.feature("Popups")
@allure.story("Validation")
class TestPopupsValidation:

    @allure.title("[Validation] Alert не меняет DOM (#confirmResult/#promptResult остаются пустыми)")
    def test_plain_alert_does_not_touch_dom(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        before_c = page.get_confirm_result()
        before_p = page.get_prompt_result()

        page.click_alert_and_accept()

        after_c = page.get_confirm_result()
        after_p = page.get_prompt_result()

        assert before_c == after_c
        assert before_p == after_p

    @allure.title("[Security] Prompt обрабатывает ввод безопасно: текст виден как текст, в HTML нет опасных конструкций")
    def test_prompt_escapes_html(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        payload = "<b>Bold</b>&\"'"
        _, visible_text = page.click_prompt_and_respond(payload, accept=True)

        expected_fragment = "Bold&\"'"
        assert expected_fragment in visible_text, (
            f"Ожидали увидеть {expected_fragment!r} в видимом тексте результата, получили: {visible_text!r}"
        )

        inner_html = page.find(page.PROMPT_RESULT).get_attribute("innerHTML") or ""

        tags = re.findall(r"<\s*/?\s*([a-z0-9]+)([^>]*)>", inner_html, flags=re.I)
        allow_tags = {"b", "strong", "i", "em"} 
        disallowed = [t for t, attrs in tags if t.lower() not in allow_tags]
        assert not disallowed, f"Найдены нежелательные теги в innerHTML: {disallowed}; innerHTML={inner_html!r}"

        dangerous = re.search(r"(on\w+\s*=|javascript:|src\s*=)", inner_html, flags=re.I)
        assert not dangerous, f"Обнаружены потенциально опасные атрибуты/скрипты в innerHTML: {inner_html!r}"

        assert "&amp;" in inner_html or "&quot;" in inner_html or "&#" in inner_html, (
            f"Ожидали HTML-экранирование спецсимволов в innerHTML, получили: {inner_html!r}"
        )
