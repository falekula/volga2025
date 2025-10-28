from __future__ import annotations
import pytest
import allure

from pages.popups_page import PopupsPage

@pytest.mark.regression
@allure.feature("Popups")
@allure.story("Regression")
class TestPopupsRegression:

    @allure.title("[REG] Confirm идемпотентность: 3x accept → стабильный результат")
    def test_confirm_idempotent_accept(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        vals = []
        for _ in range(3):
            _, txt = page.click_confirm_and_choose(accept=True)
            vals.append(txt)
        assert len(set(vals)) == 1
        assert vals[0] != ""

    @allure.title("[REG] Confirm: accept vs dismiss → разные результаты")
    def test_confirm_accept_vs_dismiss(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        _, ok_txt = page.click_confirm_and_choose(accept=True)
        _, cancel_txt = page.click_confirm_and_choose(accept=False)
        assert ok_txt and cancel_txt and ok_txt != cancel_txt

    @allure.title("[REG] Prompt: ввод текста меняет результат, dismiss не добавляет введённое значение")
    def test_prompt_text_and_dismiss(self, driver, base_url, wait_timeout):
        page = PopupsPage(driver, wait_timeout)
        page.open_and_ready(base_url)

        _, t1 = page.click_prompt_and_respond("QA1", accept=True)
        assert "QA1" in t1

        _, t2 = page.click_prompt_and_respond("WILL_BE_DISMISSED", accept=False)
        # Гарантированное условие: в результате не должно появиться новое значение
        assert "WILL_BE_DISMISSED" not in t2
