# tests/form_fields/test_quality.py
import pytest
import allure
import time
from pages.form_fields import FormPage

@pytest.mark.chrome_only
@pytest.mark.regression
@allure.feature("Form Fields")
@allure.story("Quality")
@allure.severity(allure.severity_level.CRITICAL)
def test_no_severe_console_errors_on_load_and_submit(driver, base_url, wait_timeout):
    if "chrome" not in (driver.capabilities.get("browserName","").lower()):
        pytest.skip("chrome_only: запустилось не в Chrome — пропускаем")

    NOISY_PATTERNS = (
        "deprecated_endpoint",
        "favicon", "manifest",
        "gcm", "chrome-extension",
        # доп. “шум”, который часто прилетает в Chrome:
        "Automatic fallback to software WebGL", "swiftshader", "webgl",
        "ERR_BLOCKED_BY_CLIENT", "ERR_CONNECTION_REFUSED",
    )

    def read_console(*, clear: bool = False):
        # chrome лог очищается чтением — иногда полезно «сбросить» старый шум
        if clear:
            try:
                driver.get_log("browser")
            except Exception:
                pass
        entries = driver.get_log("browser") or []
        severe = [
            e for e in entries
            if str(e.get("level", "")).upper() == "SEVERE"
            and not any(n in str(e.get("message", "")).lower() for n in map(str.lower, NOISY_PATTERNS))
        ]
        return severe, entries

    page = FormPage(driver, wait_timeout)
    page.open_and_ready(base_url)

    with allure.step("Очистить «старый» лог после загрузки и прочитать актуальный"):
        # сначала сбрасываем буфер, затем читаем «чистые» записи
        read_console(clear=True)
        severe, all_entries = read_console()
        if all_entries:
            allure.attach("\n".join(str(x) for x in all_entries), "console_on_load", allure.attachment_type.TEXT)
        assert not severe, f"SEVERE в консоли на загрузке: {severe}"

    with allure.step("Валидно заполнить и отправить форму"):
        page.fill_name("Log Watcher")
        page.select_color("Red")
        page.select_drink("Coffee")
        page.select_automation_preference("Undecided")
        epoch = int(time.time())
        page.fill_email(f"log.watcher+{epoch}@example.com")
        page.fill_message("checking console after submit")
        page.submit()
        alert_text = page.accept_alert_if_present(timeout=5)
        assert alert_text and "message received" in alert_text.lower()

    with allure.step("Проверить JS-консоль после сабмита"):
        severe, all_entries = read_console()
        if all_entries:
            allure.attach("\n".join(str(x) for x in all_entries), "console_after_submit", allure.attachment_type.TEXT)
        assert not severe, f"SEVERE в консоли после сабмита: {severe}"
