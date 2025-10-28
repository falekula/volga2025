from __future__ import annotations
import pytest
import allure

from pages.popups_page import PopupsPage

@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("Popups")
@allure.story("Smoke")
def test_smoke_all_popups(driver, base_url, wait_timeout):
    page = PopupsPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    with allure.step("Alert: появляется системный alert и принимается"):
        alert_text = page.click_alert_and_accept()
        assert alert_text is not None

    with allure.step("Confirm: accept → #confirmResult непустой"):
        _, confirm_txt_ok = page.click_confirm_and_choose(accept=True)
        assert confirm_txt_ok != ""

    with allure.step("Confirm: dismiss → текст меняется"):
        _, confirm_txt_cancel = page.click_confirm_and_choose(accept=False)
        assert confirm_txt_cancel != ""
        assert confirm_txt_cancel != confirm_txt_ok

    with allure.step("Prompt: ввести 'QA' и принять → #promptResult содержит 'QA'"):
        _, prompt_txt = page.click_prompt_and_respond("QA", accept=True)
        assert "QA" in prompt_txt
