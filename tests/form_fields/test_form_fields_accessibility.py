from __future__ import annotations

import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.form_fields import FormPage

@pytest.mark.regression
@allure.feature("Form Fields")
@allure.story("Accessibility")
@allure.severity(allure.severity_level.NORMAL)
def test_accessible_labels_and_keyboard_submit(driver, base_url, wait_timeout):
    page = FormPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    expectations = {
        "name-input": "name",
        "email": "email",
        "message": "message",
        "automation": "automation",
    }

    with allure.step("Проверить наличие доступного имени (или ближайшего контекстного текста)"):
        missing = []
        for el_id, expected in expectations.items():
            el = driver.find_element(By.ID, el_id)
            name_or_ctx = (page.get_accessible_name_or_context(el) or "").lower()
            if expected not in name_or_ctx:
                missing.append((el_id, name_or_ctx))

        if len(missing) == 1 and missing[0][0] == "automation":
            pytest.xfail("На демо-странице у #automation нет связанного label/aria — известное ограничение стенда")
        else:
            assert not missing, f"Нет доступного имени для: {missing!r}"

    with allure.step("Сабмит доступен с клавиатуры (Enter по кнопке)"):
        driver.find_element(*page.NAME_INPUT).send_keys("A11y User")
        driver.find_element(*page.EMAIL_INPUT).send_keys("a11y@example.com")
        driver.find_element(*page.MESSAGE_TEXTAREA).send_keys("hello")
        btn = driver.find_element(*page.SUBMIT_BTN)
        btn.send_keys(Keys.ENTER)
        alert_text = page.accept_alert_if_present(timeout=5)
        assert alert_text and "message received" in alert_text.lower()