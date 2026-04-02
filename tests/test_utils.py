from datetime import datetime

import pandas as pd
import pytest

from utils import calculate_total, convert_amount, filter_transactions, get_current_date, validate_date


@pytest.mark.parametrize(("date_str", "expected"), [("01.01.2026", True), ("2026-01-01", False)])
def test_validate_date(date_str: str, expected: bool) -> None:
    assert validate_date(date_str) is expected


def test_convert_amount() -> None:
    assert convert_amount(15.6) == 16


def test_get_current_date() -> None:
    value = get_current_date()
    datetime.strptime(value, "%d.%m.%Y")


def test_filter_transactions() -> None:
    dataframe = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2026-01-01", "2026-02-01"]),
            "Сумма операции": [100, 200],
        }
    )
    result = filter_transactions(dataframe, datetime(2026, 1, 15), datetime(2026, 2, 2))
    assert len(result) == 1


def test_calculate_total() -> None:
    dataframe = pd.DataFrame({"Сумма операции": [1.2, 2.2]})
    assert calculate_total(dataframe) == 3
