from __future__ import annotations

import pytest
import allure
from selenium.webdriver.common.by import By

from pages.form_fields import FormPage

@pytest.mark.regression
@allure.feature("Form Fields")
@allure.story("UX")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("control_id, is_radio", [("drink2", False), ("color2", True)])
def test_label_click_toggles_controls(driver, base_url, wait_timeout, control_id, is_radio):
    page = FormPage(driver, wait_timeout)
    page.open_and_ready(base_url)
    assert page.is_open(base_url)

    with allure.step(f"Клик по label для #{control_id} переключает контрол"):
        input_el = driver.find_element(By.CSS_SELECTOR, f"#{control_id}")
        if is_radio:
            assert not input_el.is_selected()
        page.click_label_for(control_id)
        assert input_el.is_selected()