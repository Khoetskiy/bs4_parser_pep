# 🐍 BS4 Parser PEP

![GitHub last commit](https://img.shields.io/github/last-commit/Khoetskiy/bs4_parser_pep) ![GitHub license](https://img.shields.io/github/license/Khoetskiy/bs4_parser_pep) ![GitHub top language](https://img.shields.io/github/languages/top/Khoetskiy/bs4_parser_pep) ![GitHub repo size](https://img.shields.io/github/repo-size/Khoetskiy/bs4_parser_pep) ![GitHub stars](https://img.shields.io/github/stars/Khoetskiy/bs4_parser_pep) ![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)

**Парсер документации Python** (*what's new, latest versions, download, pep*) с возможностью сбора информации о статусах PEP, скачивания документации и анализа обновлений Python.

- [🐍 BS4 Parser PEP](#-bs4-parser-pep)
  - [✨ Возможности](#-возможности)
  - [🛠️ Технологии](#️-технологии)
    - [🧪 Тестирование и качество кода](#-тестирование-и-качество-кода)
  - [⚙️ Установка](#️-установка)
  - [🚀 Использование](#-использование)
    - [Информация о новых возможностях Python](#информация-о-новых-возможностях-python)
    - [Информация о версиях Python](#информация-о-версиях-python)
    - [Скачивание документации](#скачивание-документации)
    - [Получение информации о PEP](#получение-информации-о-pep)
    - [Дополнительные параметры](#дополнительные-параметры)
  - [📋 Примеры вывода](#-примеры-вывода)
    - [Вывод статистики PEP в виде таблицы](#вывод-статистики-pep-в-виде-таблицы)
    - [Сохранение результатов в файл](#сохранение-результатов-в-файл)
    - [Очистка кеша перед выполнением](#очистка-кеша-перед-выполнением)
  - [📁 Структура проекта](#-структура-проекта)
  - [📝 Логирование](#-логирование)
  - [🧪 Тесты](#-тесты)
  - [🔍 Линтинг](#-линтинг)
  - [📄 Лицензия](#-лицензия)
  - [👨‍💻 Автор](#-автор)

## ✨ Возможности

- Парсинг и анализ статусов PEP документов
- Загрузка PDF-версии документации Python
- Получение информации о новых возможностях в разных версиях Python
- Получение информации о всех доступных версиях Python и их статусах
- Кеширование HTTP-запросов для оптимизации производительности
- Вывод результатов в различных форматах (console, file)

## 🛠️ Технологии

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=yellow) ![Requests](https://img.shields.io/badge/Requests-2.27.1-FF9A00?style=for-the-badge&logo=python&logoColor=white) ![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.9.3-4E9A06?style=for-the-badge&logo=python&logoColor=white) ![lxml](https://img.shields.io/badge/lxml-4.6.3-0B4F79?style=for-the-badge&logo=python&logoColor=white) ![Requests-Cache](https://img.shields.io/badge/Requests--Cache-1.0.0-FF6B6B?style=for-the-badge&logo=python&logoColor=white) ![PrettyTable](https://img.shields.io/badge/PrettyTable-2.1.0-CC7722?style=for-the-badge&logo=python&logoColor=white) ![TQDM](https://img.shields.io/badge/tqdm-4.61.0-FFD43B?style=for-the-badge&logo=python&logoColor=black)

### 🧪 Тестирование и качество кода

![Pytest](https://img.shields.io/badge/Pytest-7.1.0-0A9EDC?style=for-the-badge&logo=pytest&logoColor=green) ![Flake8](https://img.shields.io/badge/Flake8-4.0.1-007ACC?style=for-the-badge&logo=python&logoColor=red) ![Ruff](https://img.shields.io/badge/Ruff-0.12.12-000000?style=for-the-badge&logo=ruff&logoColor=perpl)

## ⚙️ Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Khoetskiy/bs4_parser_pep.git
cd bs4_parser_pep
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

> **💡Альтернатива**: используйте [uv](https://github.com/astral-sh/uv) для создания виртуального окружения и установки зависимостей:

```bash
uv init
uv venv
uv pip install -r requirements.txt
```

## 🚀 Использование

Парсер поддерживает несколько режимов работы, указываемых через аргументы командной строки:

### Информация о новых возможностях Python

```bash
python main.py whats-new
```

Собирает информацию о новых возможностях из разных версий Python.

### Информация о версиях Python

```bash
python main.py latest-versions
```

Получает информацию о доступных версиях Python и их статусах.

### Скачивание документации

```bash
python main.py download
```

Скачивает PDF-версию документации Python в директорию downloads/.

### Получение информации о PEP

```bash
python main.py pep
```

Собирает информацию о статусах PEP документов и выводит статистику.

### Дополнительные параметры

|Параметр|Короткая форма|Описание|
|---|---|---|
|`--help`|`-h`| Показать справку по использованию|
|`--clear-cache`|`-c`| Очистка кеша перед выполнением|
|`--output {pretty,file}`|`-o {pretty,file}`| Формат вывода|

**Варианты вывода:**

- По умолчанию: стандартный вывод в консоль
- `pretty`: красивый табличный вывод в консоль
- `file`: сохранение результатов в CSV файл с временной меткой

## 📋 Примеры вывода

### Вывод статистики PEP в виде таблицы

```bash
python main.py pep --output pretty
```

**Результат:**

```bash
+------------------+------------+
| Статус           | Количество |
+------------------+------------+
| Accepted         | 20         |
| Active           | 35         |
| April Fool!      | 1          |
| Deferred         | 38         |
| Draft            | 42         |
| Final            | 340        |
| Provisional      | 1          |
| Rejected         | 126        |
| Superseded       | 25         |
| Withdrawn        | 68         |
| Total            | 696        |
+------------------+------------+
```

### Сохранение результатов в файл

```bash
python main.py whats-new -o file
```

Файл сохраняется в `src/results/` с именем в формате: `whats-new_2025-09-06_01-21-05.csv`

### Очистка кеша перед выполнением

```bash
python main.py latest-versions -c
```

Полезно для получения актуальной информации или при проблемах с кешированными данными.

## 📁 Структура проекта

```bash
bs4_parser_pep/
├── src/
│   ├── __init__.py
│   ├── configs.py      # Конфигурация логирования и аргументов
│   ├── constants.py    # Константы и настройки
│   ├── exceptions.py   # Кастомные исключения
│   ├── main.py        # Основной скрипт
│   ├── outputs.py     # Форматирование вывода
│   └── utils.py       # Вспомогательные функции
├── tests/
├── .flake8
├── pytest.ini
├── requirements.txt
├── pyproject.toml
├── uv.lock
└── README.md
└── LICENSE
```

## 📝 Логирование

Логи работы парсера сохраняются в директории `src/logs/`:

- Информация о запуске и завершении работы
- Предупреждения о несоответствии статусов PEP
- Ошибки при загрузке страниц или парсинге

## 🧪 Тесты

Для запуска тестов используйте:

```bash
pytest
```

## 🔍 Линтинг

Проект использует [ruff](https://github.com/astral-sh/ruff) для проверки качества кода. Конфигурация находится в `pyproject.toml`.

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## 👨‍💻 Автор

**GitHub:** [@Khoetskiy](https://github.com/Khoetskiy)

---

⭐ Если проект оказался полезным, поставьте звездочку!
