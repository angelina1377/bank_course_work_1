"""Сервисы для анализа транзакций."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

LOGGER = logging.getLogger(__name__)
DATE_COLUMN = "Дата операции"
AMOUNT_COLUMN = "Сумма операции"
CATEGORY_COLUMN = "Категория"
CASHBACK_COLUMN = "кэшбек"


def load_excel_data(file_path: str | Path = "data/operations.xlsx") -> pd.DataFrame:
    """Функция загрузки данных.

    Args:
        file_path: Path to the source Excel file.

    Returns:
        DataFrame with parsed `Дата операции` column.
    """
    resolved_path = Path(file_path)
    LOGGER.info("Loading data from %s", resolved_path)
    dataframe = pd.read_excel(resolved_path)
    dataframe[DATE_COLUMN] = pd.to_datetime(dataframe[DATE_COLUMN])
    return dataframe


def calculate_period(date_str: str, period: str = "M") -> tuple[datetime, datetime]:
    """Функция расчета периода.

    Args:
        date_str: Date in format ``DD.MM.YYYY``.
        period: One of ``W`` (week), ``M`` (month), ``Y`` (year), ``ALL``.

    Returns:
        Inclusive period boundaries.
    """
    date_value = datetime.strptime(date_str, "%d.%m.%Y")
    normalized_period = period.upper()

    if normalized_period == "W":
        start_date = date_value - timedelta(days=date_value.weekday())
        end_date = start_date + timedelta(days=6)
    elif normalized_period == "M":
        start_date = date_value.replace(day=1)
        end_date = date_value
    elif normalized_period == "Y":
        start_date = date_value.replace(month=1, day=1)
        end_date = date_value
    elif normalized_period == "ALL":
        start_date = datetime.min
        end_date = date_value
    else:
        raise ValueError("Неверный период. Поддерживаются: W, M, Y, ALL")

    return start_date, end_date


def get_transactions_by_date(dataframe: pd.DataFrame, date_value: datetime) -> pd.DataFrame:
    """Функция фильтрации транзакций."""
    return dataframe[dataframe[DATE_COLUMN].dt.date == date_value.date()]


def analyze_cashback_categories(data: pd.DataFrame, year: int, month: int) -> dict[str, float]:
    """Функция анализа категорий кэшбэка.

    Учитываются только расходные операции (`Сумма операции < 0`).
    """
    filtered_data = data[
        (data[DATE_COLUMN].dt.year == year)
        & (data[DATE_COLUMN].dt.month == month)
        & (data[AMOUNT_COLUMN] < 0)
    ]
    category_sums = filtered_data.groupby(CATEGORY_COLUMN).apply(
        lambda frame: (frame[AMOUNT_COLUMN].abs() * frame[CASHBACK_COLUMN] / 100).sum()
    )
    return {category: round(amount, 2) for category, amount in category_sums.to_dict().items()}


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """Функция расчета инвестиций банка.

    Args:
        month: Любая строка даты.
        transactions: Список словарей транзакций.
        limit: Округляем (должно быть положительным числом).
    """
    if limit <= 0:
        raise ValueError("Параметр limit должен быть больше 0")

    if not transactions:
        return 0.0

    total = 0.0
    target_month = pd.to_datetime(month).date().replace(day=1)

    for transaction in transactions:
        transaction_date = pd.to_datetime(transaction[DATE_COLUMN]).date()
        if transaction_date.replace(day=1) != target_month:
            continue

        amount = float(transaction[AMOUNT_COLUMN])
        if amount >= 0:
            continue

        positive_amount = abs(amount)
        rounded = ((positive_amount + limit - 1) // limit) * limit
        total += rounded - positive_amount

    return round(total, 2)
