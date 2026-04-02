"""Функции создания отчетов с декоратором."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import pandas as pd

DATE_COLUMN = "Дата операции"
AMOUNT_COLUMN = "Сумма операции"
CATEGORY_COLUMN = "Категория"


def report_decorator(filename: str = "report.json") -> Callable[..., Any]:
    """Декоратор."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)
            Path(filename).write_text(
                json.dumps(result.to_dict(orient="records"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: datetime | None = None,
) -> pd.DataFrame:
    """Отчет о расходах за 90 дней для выбранной категории."""
    report_date = date or datetime.now()
    start_date = report_date - timedelta(days=90)

    filtered_df = transactions[
        (transactions[DATE_COLUMN] >= start_date)
        & (transactions[DATE_COLUMN] <= report_date)
        & (transactions[CATEGORY_COLUMN] == category)
    ]

    return pd.DataFrame(
        {
            "Категория": [category],
            "Общие траты": [int(round(-filtered_df[AMOUNT_COLUMN].sum()))],
            "Период": [f"{start_date.date()} - {report_date.date()}"],
        }
    )


@report_decorator("weekly_report.json")
def weekly_spending_report(transactions: pd.DataFrame, date: datetime | None = None) -> pd.DataFrame:
    """Отчет о расходах по дням недели."""
    report_date = date or datetime.now()
    start_date = report_date - timedelta(days=90)

    filtered_df = transactions[
        (transactions[DATE_COLUMN] >= start_date) & (transactions[DATE_COLUMN] <= report_date)
    ]
    result = (
        filtered_df.groupby(filtered_df[DATE_COLUMN].dt.day_name())[AMOUNT_COLUMN]
        .sum()
        .mul(-1)
        .round()
        .astype(int)
        .reset_index()
    )
    return result.rename(columns={DATE_COLUMN: "День недели", AMOUNT_COLUMN: "Сумма"})


@report_decorator("work_weekend_report.json")
def work_weekend_report(transactions: pd.DataFrame, date: datetime | None = None) -> pd.DataFrame:
    """Распределение расходов на рабочие дни."""
    report_date = date or datetime.now()
    start_date = report_date - timedelta(days=90)
    filtered_df = transactions[
        (transactions[DATE_COLUMN] >= start_date) & (transactions[DATE_COLUMN] <= report_date)
    ].copy()

    filtered_df["is_weekend"] = filtered_df[DATE_COLUMN].dt.weekday >= 5
    work_spending = -filtered_df.loc[~filtered_df["is_weekend"], AMOUNT_COLUMN].sum()
    weekend_spending = -filtered_df.loc[filtered_df["is_weekend"], AMOUNT_COLUMN].sum()

    return pd.DataFrame(
        {
            "Тип дня": ["Рабочие дни", "Выходные"],
            "Общие траты": [int(round(work_spending)), int(round(weekend_spending))],
        }
    )