from __future__ import annotations

import pytest
import allure

from pages.form_fields import FormPage

@pytest.mark.regression
@allure.feature("Form Fields")
@allure.story("Validation")
@allure.severity(allure.severity_level.CRITICAL)
def test_email_native_validity_flags(driver, base_url, wait_timeout):
    page = FormPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    email = driver.find_element(*page.EMAIL_INPUT)
    input_type = (email.get_attribute("type") or "").lower()

    if input_type != "email":
        pytest.xfail(f"Поле #email имеет type='{input_type}', а не 'email' — HTML5-валидации нет на этом стенде")

    with allure.step("Невалидный email → checkValidity()==false"):
        email.clear()
        email.send_keys("not-an-email")
        valid = driver.execute_script("return arguments[0].checkValidity();", email)
        msg = driver.execute_script("return arguments[0].validationMessage;", email) or ""
        assert valid is False
        assert msg != ""

    with allure.step("Валидный email → checkValidity()==true"):
        email.clear()
        email.send_keys("valid@example.com")
        valid2 = driver.execute_script("return arguments[0].checkValidity();", email)
        assert valid2 is True