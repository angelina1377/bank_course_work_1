import pandas as pd

from src.services import analyze_cashback_categories, calculate_period, investment_bank


def test_calculate_period_month():
    start, end = calculate_period("20.05.2020", "M")
    assert start == start.replace(day=1)
    assert end.day == 20 and end.month == 5 and end.year == 2020


def test_calculate_period_week_is_capped_by_date():
    start, end = calculate_period("20.05.2020", "W")
    assert start.weekday() == 0  # Monday
    assert end.strftime("%d.%m.%Y") == "20.05.2020"


def test_calculate_period_year():
    start, end = calculate_period("20.05.2020", "Y")
    assert start.strftime("%d.%m.%Y") == "01.01.2020"
    assert end.strftime("%d.%m.%Y") == "20.05.2020"


def test_calculate_period_all():
    start, end = calculate_period("20.05.2020", "ALL")
    assert start.year == 1
    assert end.strftime("%d.%m.%Y") == "20.05.2020"


def test_analyze_cashback_categories_sums_cashback_column():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2020-05-01", "2020-05-02", "2020-06-01"]),
            "Сумма операции": [-100, -200, -300],
            "Категория": ["A", "A", "B"],
            "Кешбэк": [5.4, 4.6, 100],
        }
    )
    out = analyze_cashback_categories(df, 2020, 5)
    assert out == {"A": 10}


def test_investment_bank_rounding():
    tx = [
        {"Дата операции": "2020-05-01", "Сумма операции": -1712},
        {"Дата операции": "2020-05-10", "Сумма операции": -50},
        {"Дата операции": "2020-06-01", "Сумма операции": -1712},
        {"Дата операции": "2020-05-20", "Сумма операции": 1000},
    ]
    assert investment_bank("2020-05", tx, 50) == 38.0
