# Bank Course Work 1

Небольшое консольное приложение для анализа банковских операций из Excel и формирования сводки (доходы/расходы), а также получения актуальных курсов валют и цен акций по спискам пользователя.

## Возможности

- **Сводка за период**: расходы (топ‑категории + «Переводы/Наличные») и доходы (топ‑категории).
- **Курсы валют**: по списку из `user_settings.json` (через `exchangerate-api.com`).
- **Цены акций**: по списку из `user_settings.json` (через `polygon.io`).
- **Отчёты (DataFrame → JSON)**: функции в `src/reports.py` сохраняют результат в JSON через декоратор.

## Требования

- Python **3.14+**
- Poetry

## Установка

1. Установите Poetry по инструкции: `https://python-poetry.org/docs/#installation`
2. Установите зависимости:

```bash
poetry install
```

Чтобы поставить зависимости для разработки (тесты/flake8):

```bash
poetry install --with dev
```

## Данные и конфигурация

Перед запуском убедитесь, что в корне проекта есть:

- **Файл данных**: `data/operations.xlsx`
  - приложение читает его из `src/services.py` (путь `data/operations.xlsx`)
  - ожидаются колонки (используются в коде): `Дата операции`, `Сумма операции`, `Категория`, `кэшбек`
- **Настройки пользователя**: `user_settings.json`
  - `user_currencies`: список валют (например `["USD", "EUR"]`)
  - `user_stocks`: список тикеров акций (например `["AAPL", "MSFT"]`)
- **Переменные окружения**: `.env` (не коммитится)
  - `CURRENCY_API_KEY` (в коде переменная читается, но текущий URL валют не требует ключа)
  - `STOCK_API_KEY` (ключ для Polygon)

Пример `.env`:

```env
STOCK_API_KEY=YOUR_KEY_HERE
CURRENCY_API_KEY=OPTIONAL
```

## Запуск

Точка входа — `src/main.py`. Команда ожидает дату и опционально период:

```bash
poetry run python src/main.py 18.03.2026 M
```

Где период:

- `W` — неделя
- `M` — месяц (по умолчанию)
- `Y` — год
- `ALL` — все данные до указанной даты

Результат печатается в stdout в формате JSON.

## Отчёты из `src/reports.py`

Функции возвращают `pandas.DataFrame` и автоматически сохраняют JSON рядом с запуском:

- `spending_by_category(...)` → `report.json`
- `weekly_spending_report(...)` → `weekly_report.json`
- `work_weekend_report(...)` → `work_weekend_report.json`

## Тестирование

```bash
poetry run pytest
```

## Проверка стиля

```bash
poetry run flake8
```

