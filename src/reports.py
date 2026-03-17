from __future__ import annotations # включает отложенное разрешение аннотаций типов

import json # работа с JSON‑файлами
from datetime import datetime, timedelta # работа с датами и временными интервалами
from functools import wraps # декоратор, который сохраняет метаданные исходной функции (имя, документацию) при декорировании
from pathlib import Path # объектно‑ориентированная работа с путями к файлам
from typing import Any, Callable, Optional, TypeVar # аннотации типов

import pandas as pd # работа с табличными данными (DataFrame): фильтрация, группировка, агрегация

T = TypeVar("T") # позволяет декоратору работать с функциями, возвращающими любой тип данных

# декоратор для функций‑отчётов
def report_decorator(filename: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Декоратор для функций-отчетов.
    - Без параметра: пишет результат в файл с именем по умолчанию (на основе имени функции и времени).
    - С параметром: пишет в указанный файл.
    """
# внутренняя функция, которая принимает функцию func и возвращает обёртку wrapper
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func) # сохраняет метаданные func (имя, документацию) после декорирования
        def wrapper(*args: Any, **kwargs: Any) -> T: # обёртка
            result = func(*args, **kwargs)

            out_name = filename
            if not out_name:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_name = f"report_{func.__name__}_{ts}.json" # генерирует имя по шаблону: report_{имя_функции}_{текущее_время}.json

            path = Path(out_name) # Создаёт объект Path для работы с файлом

            if isinstance(result, pd.DataFrame):
                if path.suffix.lower() == ".xlsx":
                    result.to_excel(path, index=False)
                else:
                    with path.open("w", encoding="utf-8") as f:
                        json.dump(result.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
            else:
                with path.open("w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

            return result

        return wrapper

    return decorator


@report_decorator()
# анализирует траты по конкретной категории за последние 90 дней
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    end_date = datetime.now() if date is None else _parse_date(date)
    start_date = end_date - timedelta(days=90)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    filtered_df = df[
        (df["Дата операции"] >= start_date)
        & (df["Дата операции"] <= end_date)
        & (df["Категория"] == category)
        & (df["Сумма операции"] < 0)
    ]
# Считает сумму расходов (умножает на -1, чтобы получить положительное число)
    spending = int(round((-filtered_df["Сумма операции"]).sum()))
# Возвращает DataFrame с итоговыми данными
    return pd.DataFrame(
        {
            "Категория": [category],
            "Траты": [spending],
            "Период": [f"{start_date.date()} - {end_date.date()}"],
        }
    )

@report_decorator("weekly_report.json")  # С параметром — кастомное имя файла
# строит отчёт о тратах по дням недели за последние 90 дней
def weekly_spending_report(transactions: pd.DataFrame,
                           date: Optional[str] = None) -> pd.DataFrame:
    end_date = datetime.now() if date is None else _parse_date(date)
    start_date = end_date - timedelta(days=90)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

    weekly_spending = (
        filtered_df.groupby(filtered_df["Дата операции"].dt.day_name())["Сумма операции"]
        .sum()
        .apply(lambda x: round(x * -1))
        .reset_index()
    )
    return weekly_spending

@report_decorator("work_weekend_report.json")
# сравнивает траты в рабочие дни и выходные за последние 90 дней
def work_weekend_report(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    end_date = datetime.now() if date is None else _parse_date(date)
    start_date = end_date - timedelta(days=90)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)].copy()
    filtered_df["IsWeekend"] = filtered_df["Дата операции"].dt.weekday >= 5

    work_spending = (-filtered_df[~filtered_df["IsWeekend"]]["Сумма операции"].sum())
    weekend_spending = (-filtered_df[filtered_df["IsWeekend"]]["Сумма операции"].sum())

    return pd.DataFrame(
        {
            "Тип дня": ["Рабочие дни", "Выходные"],
            "Траты": [round(work_spending), round(weekend_spending)],
        }
    )

# Вспомогательная функция
def _parse_date(date_str: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y") # перебирает два формата даты
        try:
            return datetime.strptime(date_str, fmt) # метод, который преобразует строку в объект datetime согласно заданному формату fmt
        except ValueError:
            continue
    raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD или ДД.ММ.ГГГГ")