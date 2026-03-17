from datetime import datetime

import pandas as pd

from src.utils import filter_transactions, validate_date


def test_validate_date_ok():
    assert validate_date("20.05.2020") is True


def test_validate_date_bad():
    assert validate_date("2020-05-20") is False
    assert validate_date("xx") is False


def test_filter_transactions_by_range():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2020-05-01", "2020-05-10", "2020-06-01"]),
            "Сумма операции": [1, 2, 3],
        }
    )
    out = filter_transactions(
        df,
        start_date=datetime(2020, 5, 1),
        end_date=datetime(2020, 5, 31),
    )
    assert out["Сумма операции"].tolist() == [1, 2]
