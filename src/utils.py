"""Общие полезные функции."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def validate_date(date_str: str) -> bool:
    """Функция валидации даты `DD.MM.YYYY` format."""
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def convert_amount(amount: float) -> int:
    """Функция конвертации суммы."""
    return round(amount)


def get_current_date() -> str:
    """Функция получения текущей даты `DD.MM.YYYY` string."""
    return datetime.now().strftime("%d.%m.%Y")


def filter_transactions(dataframe: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Функция фильтрации транзакций."""
    return dataframe[
        (dataframe["Дата операции"] >= start_date) & (dataframe["Дата операции"] <= end_date)
    ]


def calculate_total(dataframe: pd.DataFrame) -> int:
    """Подсчет общей суммы."""
    return round(dataframe["Сумма операции"].sum())