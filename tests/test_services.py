from datetime import datetime

import pandas as pd
import pytest

from services import (
    analyze_cashback_categories,
    calculate_period,
    get_transactions_by_date,
    investment_bank,
)


@pytest.fixture
def transactions_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["2026-02-01", "2026-02-03", "2026-02-03", "2026-03-01"]
            ),
            "Сумма операции": [-100.0, -50.0, 150.0, -20.0],
            "Категория": ["Еда", "Такси", "Зарплата", "Еда"],
            "кэшбек": [1.0, 3.0, 0.0, 1.0],
        }
    )


@pytest.mark.parametrize(
    ("period", "start", "end"),
    [
        ("M", datetime(2026, 2, 1), datetime(2026, 2, 10)),
        ("Y", datetime(2026, 1, 1), datetime(2026, 2, 10)),
        ("W", datetime(2026, 2, 9), datetime(2026, 2, 15)),
    ],
)
def test_calculate_period(period: str, start: datetime, end: datetime) -> None:
    start_date, end_date = calculate_period("10.02.2026", period)
    assert start_date == start
    assert end_date == end


def test_calculate_period_all() -> None:
    start_date, end_date = calculate_period("10.02.2026", "ALL")
    assert start_date == datetime.min
    assert end_date == datetime(2026, 2, 10)


def test_calculate_period_invalid_period() -> None:
    with pytest.raises(ValueError):
        calculate_period("10.02.2026", "Q")


def test_get_transactions_by_date(transactions_df: pd.DataFrame) -> None:
    result = get_transactions_by_date(transactions_df, datetime(2026, 2, 3))
    assert len(result) == 2


def test_analyze_cashback_categories(transactions_df: pd.DataFrame) -> None:
    result = analyze_cashback_categories(transactions_df, 2026, 2)
    assert result == {"Еда": 1.0, "Такси": 1.5}


def test_investment_bank_happy_path() -> None:
    transactions = [
        {"Дата операции": "2026-02-01", "Сумма операции": -79},
        {"Дата операции": "2026-02-04", "Сумма операции": -150},
        {"Дата операции": "2026-03-01", "Сумма операции": -70},
        {"Дата операции": "2026-02-05", "Сумма операции": 1000},
    ]
    assert investment_bank("2026-02-01", transactions, 100) == 71.0


def test_investment_bank_empty() -> None:
    assert investment_bank("2026-02-01", [], 100) == 0.0


def test_investment_bank_invalid_limit() -> None:
    with pytest.raises(ValueError):
        investment_bank("2026-02-01", [], 0)
