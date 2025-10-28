# UI‑автотесты Practice Automation

Репозиторий с UI‑тестами на **Python 3.12 + Selenium + Pytest + Allure**. Пакет покрывает страницы **Click Events**, **Popups** и **Form Fields** на учебном стенде [practice-automation.com](https://practice-automation.com/), демонстрируя структурированный подход (Page Object Model), чистые сценарии и удобные пресеты запуска.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" />
  <img alt="Selenium" src="https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white" />
  <img alt="Pytest" src="https://img.shields.io/badge/Pytest-%E2%9C%93-0A9EDC?logo=pytest&logoColor=white" />
  <img alt="Allure" src="https://img.shields.io/badge/Allure-Reports-F16822?logo=allure&logoColor=white" />
</p>

---

## 📋 Содержание

* <a href="#что-покрыто">🎯 Что покрыто</a>
* <a href="#технологии-и-требования">🛠 Технологии и требования</a>
* <a href="#установка">⚙️ Установка</a>
* <a href="#быстрый-старт">🚀 Быстрый старт</a>
* <a href="#фильтрация">🎮 Фильтрация по маркерам и ключевым словам</a>
* <a href="#отчёты-allure">📊 Отчёты Allure</a>
* <a href="#архитектура-и-подход">🏗 Архитектура и подход</a>
* <a href="#структура-проекта">📁 Структура проекта</a>
* <a href="#ci-github-actions-пример">🔧 CI: GitHub Actions пример</a>

---

<a id="что-покрыто"></a>
## 🎯 Что покрыто

### 📍 Click Events
Страница с кнопками *Cat*, *Dog*, *Pig*, *Cow* и live‑output `#demo`:
* **Smoke**: клик по каждой кнопке показывает корректный текст
* **Content**: текст заголовка H1, подписи кнопок, точность сообщений
* **Accessibility**: активация клавишами Space/Enter, live‑region
* **UX**: отзывчивость ≤500 мс, видимость кнопок
* **Regression**: идемпотентность, стабильность порядка

### 🪟 Popups
Страница с Alert, Confirm, Prompt и Tooltip:
* **Smoke**: базовое взаимодействие с попапами
* **Quality**: отсутствие SEVERE ошибок в консоли
* **Accessibility**: клавиатурная навигация
* **UX**: скорость появления алертов, работа tooltip
* **Validation**: безопасность ввода, неизменность DOM
* **Regression**: идемпотентность Confirm, различие accept/dismiss

### 📝 Form Fields
Страница с формой обратной связи:
* **Smoke**: базовое заполнение и отправка
* **Quality**: отсутствие SEVERE ошибок при загрузке и отправке
* **Accessibility**: доступные имена полей, клавиатурный сабмит
* **UX**: клик по label переключает контролы
* **Validation**: HTML5 валидация email
* **Regression**: комплексное заполнение всех полей

---

<a id="технологии-и-требования"></a>
## 🛠 Технологии и требования

* **Язык**: Python 3.12+
* **Фреймворк**: Pytest (+ маркеры `smoke`, `regression`, `chrome_only`, `firefox_only`)
* **UI**: Selenium 4.x (Chrome/Firefox; поддержан headless)
* **Отчёты**: Allure
* **Зависимости**: 
  ```txt
  selenium==4.15.0
  webdriver-manager==4.0.1
  pytest==7.4.3
  allure-pytest==2.13.2
  pytest-xdist==3.5.0
  ```

---

<a id="установка"></a>
## ⚙️ Установка

```bash
# 1) Клонирование
git clone <ваш-репозиторий> && cd <ваш-репозиторий>

# 2) Виртуальное окружение
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (macOS/Linux)
source venv/bin/activate

# 3) Зависимости
pip install -U pip
pip install -r requirements.txt

# Деактивация (когда закончишь работу)
deactivate
```

---
<a id="быстрый-старт"></a>
## 🚀 Быстрый старт

### 🎯 Базовые запуски

**Смоук по двум браузерам**
```bash
pytest -m smoke --browser=both
```

**Полная регрессия (Chrome по умолчанию)**
```bash
pytest -m regression
```

**Вся группа тестов для Form Fields**
```bash
pytest tests/form_fields
```

**Конкретный файл / конкретный тест**
```bash
# один файл
pytest tests/form_fields/test_validation.py

# один тест из файла
pytest tests/form_fields/test_validation.py::test_email_native_validity_flags
```
<a id="фильтрация"></a>
### 🎮 Фильтрация по маркерам и ключевым словам

**Смоук ИЛИ регрессия**
```bash
pytest -m "smoke or regression"
```

**Всё, кроме смоука**
```bash
pytest -m "not smoke"
```

**По ключевому слову (название теста/класса/файла)**
```bash
pytest -k "accessibility and not console"
```

### 🌐 Браузеры и режимы

**Явно указать браузер**
```bash
pytest --browser=chrome
pytest --browser=firefox
```

**Оба браузера + headless**
```bash
pytest --browser=both --headless
```

**Переопределить базовый URL, таймауты и размер окна**
```bash
pytest -m smoke --browser=chrome --base-url=https://practice-automation.com --wait-timeout=15 --window-width=1366 --window-height=768
```

### ⚡ Параллельный запуск

**Параллельно по числу ядер**
```bash
pytest -m regression -n auto
```

**Параллельно и по двум браузерам**
```bash
pytest -m regression --browser=both -n auto
```

> ⚠️ Параллельность включайте для независимых тестов. Если страница «шумная», используйте `-n 1`.

### 🔧 Отладка и диагностика

**Только собрать список тестов (без запуска)**
```bash
pytest --collect-only -q
```

**Менее/более подробный вывод**
```bash
pytest -q          # тише
pytest -vv         # очень подробно
```

**Запуск с CI-конфигом**
```bash
pytest -c pytest.ci.ini -m "smoke or regression" --browser=both
```

---

## 🎯 Быстрые пресеты

- **Перед коммитом**
  ```bash
  pytest -m smoke --browser=both --headless
  ```

- **Ночная регрессия**
  ```bash
  pytest -c pytest.ci.ini -m regression --browser=both -n auto
  ```

- **Разработка конкретного сценария**
  ```bash
  pytest tests/form_fields/test_validation.py::test_email_native_validity_flags -vv
  ```

---
<a id="отчёты-allure"></a>
## 📊 Отчёты Allure

> В `pytest.ini` уже прописано `--alluredir=allure-results`, поэтому параметр можно не повторять.

**Сгенерировать отчёт и открыть**
```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

**Быстрый просмотр (временный сервер)**
```bash
allure serve allure-results
```

---
<a id="архитектура-и-подход"></a>
## 🏗 Архитектура и подход

**Page Object Model** с базовой страницей и специализированными страницами:

* `BasePage` — единая точка ожиданий и действий:
  * безопасные `find/finds`, `wait_visible/clickable/invisible`
  * клики с fallback на JS + аккуратный `scrollIntoView`
  * ввод текста с очисткой (в т.ч. через `Ctrl+A` → `Backspace`)
  * проверки `is_visible/exists`, выполнение `js`
  * утилиты для работы с JS‑alert (`accept`/`dismiss`) и снятие скриншота

* Специализированные Page Objects:
  * `ClickEventsPage` — кнопки животных и live-регион
  * `PopupsPage` — Alert, Confirm, Prompt, Tooltip
  * `FormPage` — поля формы, чекбоксы, радиокнопки, селекты

Тесты структурированы по тематике (Smoke/Quality/Accessibility/UX/Validation/Regression) и явно раскрашены **feature/story/title** для отчётов.

---
<a id="структура-проекта"></a>
## 📁 Структура проекта

```
.
├── pages/
│   ├── base_page.py              # Базовый класс страницы
│   ├── click_events.py           # Страница Click Events
│   ├── popups_page.py            # Страница Popups
│   └── form_fields.py            # Страница Form Fields
├── tests/
│   ├── click_events/             # Тесты для Click Events
│   │   ├── test_smoke.py
│   │   ├── test_content.py
│   │   ├── test_accessibility.py
│   │   ├── test_ux.py
│   │   └── test_regression.py
│   ├── popups/                   # Тесты для Popups
│   │   ├── test_smoke.py
│   │   ├── test_quality.py
│   │   ├── test_accessibility.py
│   │   ├── test_ux.py
│   │   ├── test_validation.py
│   │   └── test_regression.py
│   └── form_fields/              # Тесты для Form Fields
│       ├── test_smoke.py
│       ├── test_quality.py
│       ├── test_accessibility.py
│       ├── test_ux.py
│       ├── test_validation.py
│       └── test_regression.py
├── conftest.py                   # Фикстуры Pytest
├── pytest.ini                    # Общие опции Pytest / Allure
├── pytest.ci.ini                 # Строгий конфиг для CI
├── requirements.txt              # Зависимости
└── README.md                     # Этот файл
```

---
<a id="ci-github-actions-пример"></a>
## 🔧 CI: GitHub Actions пример

`.github/workflows/tests.yml`

```yaml
name: ui-tests

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
      - name: Run smoke (headless, both browsers)
        run: pytest -m smoke --browser=both --headless -q
      - name: Upload allure raw results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results
          path: allure-results
```

---

## 💡 Примечания

* По умолчанию базовый URL: `https://practice-automation.com` (можно переопределить `--base-url`)
* Для нестабильных стендов допускается `pytest -n 1` (без параллели)
* В отчётах допускаются `xfail` для известных ограничений (например, live‑region или отсутствие HTML5 валидации)
* Все тесты снабжены подробными шагами и аттачментами для лёгкой отладки

---

**Готово к использованию!** 🎉
