from __future__ import annotations

import pytest
import allure
from pages.form_fields import FormPage

@pytest.mark.smoke
@allure.title("[Smoke][Form Fields] Страница открывается, элементы интерактивны, сабмит возвращает алерт")
def test_form_fields_smoke(driver, base_url, wait_timeout):
    page = FormPage(driver, wait_timeout)

    with allure.step("Открыть URL и убедиться, что это Form Fields"):
        page.open(f"{base_url}/form-fields/")
        assert page.is_open(base_url), f"Открыта не та страница. current_url={driver.current_url}"

    with allure.step("Проверить заголовок H1 содержит 'Form Fields'"):
        h1 = page.get_h1_text().lower()
        assert "form fields" in h1, f"Не нашли ожидаемый H1. Получили: {h1!r}"

    with allure.step("Ключевые элементы видимы и доступны"):
        assert page.is_visible(page.NAME_INPUT), "Поле Name недоступно"
        assert page.is_visible(page.EMAIL_INPUT), "Поле Email недоступно"
        assert page.is_visible(page.MESSAGE_TEXTAREA), "Поле Message недоступно"
        assert page.is_visible(page.SUBMIT_BTN), "Кнопка Submit недоступна"

    with allure.step("Заполнить базовые поля и выполнить простые выборы"):
        page.fill_name("Smoke User")
        page.select_color("Blue")
        page.select_drink("Milk")
        page.select_automation_preference("Yes")
        page.fill_email("smoke@example.com")
        page.fill_message("smoke")

    with allure.step("Нажать Submit и проверить алерт"):
        page.submit()
        alert_text = page.accept_alert_if_present(timeout=5)
        assert alert_text and "message received" in alert_text.lower(), (
            f"Ожидали алерт 'Message received!', фактически: {alert_text!r}"
        )

    with allure.step("Убедиться, что URL остался на /form-fields"):
        assert "/form-fields" in driver.current_url, "После отправки произошёл неожиданный редирект"
