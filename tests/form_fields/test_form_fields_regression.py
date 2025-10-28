from __future__ import annotations

import time
import pytest
import allure

from pages.form_fields import FormPage

@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("Form Fields")
@allure.story("Regression")
@allure.severity(allure.severity_level.CRITICAL)
def test_form_fill_and_submit_with_tools_list(driver, base_url, wait_timeout):
    caps = driver.capabilities or {}
    browser = str(caps.get("browserName", "")).capitalize()
    version = caps.get("browserVersion") or caps.get("version") or "?"
    allure.dynamic.title(f"[Form][{browser} {version}] Заполнение формы + Message из Automation Tools")

    page = FormPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    with allure.step("Заполнить базовые поля"):
        page.fill_name("John QA")
        page.fill_password("P@ssw0rd!")

    with allure.step("Выбрать любимый напиток и цвет"):
        page.select_drink("Milk")
        page.select_color("Blue")

    with allure.step("Выбрать 'Do you like automation?' = Yes"):
        page.select_automation_preference("yes")

    with allure.step("Отметить инструменты автоматизации (если чекбоксы присутствуют)"):
        try:
            page.toggle_tool("Selenium", check=True)
            page.toggle_tool("Cypress", check=True)
        except Exception:
            pass

    with allure.step("Сформировать Message из списка 'Automation tools' на странице"):
        tools = page.get_all_tools()
        msg = "\n".join(tools) if tools else "No tools found on page"
        page.fill_message(msg)

    with allure.step("Ввести валидный Email"):
        epoch = int(time.time())
        page.fill_email(f"john.qa+{epoch}@example.com")

    with allure.step("Отправить форму"):
        page.submit()

    with allure.step("Если появился JS-алерт — зафиксировать и закрыть"):
        alert_text = page.accept_alert_if_present(timeout=5)
        if alert_text is not None:
            assert "message received" in alert_text.lower()

    with allure.step("Валидация: нет видимых предупреждений и URL не изменился"):
        visible_warnings = page.visible_warnings()
        assert not visible_warnings
        assert "/form-fields" in driver.current_url