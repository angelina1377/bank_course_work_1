from unittest.mock import Mock, patch

import pandas as pd
import pytest

from views import (
    get_currency_rates,
    get_events_data,
    get_stock_prices,
    process_expenses,
    process_income,
)


@pytest.fixture
def operations_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["2026-02-01", "2026-02-03", "2026-02-06", "2026-02-10"]
            ),
            "Сумма операции": [-100, -20, 1000, -40],
            "Категория": ["Еда", "Наличные", "Зарплата", "Переводы"],
        }
    )


def test_process_expenses(operations_df: pd.DataFrame) -> None:
    result = process_expenses(operations_df[operations_df["Сумма операции"] < 0])
    assert result["total_amount"] == 160
    assert {"category": "Еда", "amount": 100} in result["main"]
    assert {"category": "Наличные", "amount": 20} in result["transfers_and_cash"]


def test_process_income(operations_df: pd.DataFrame) -> None:
    result = process_income(operations_df[operations_df["Сумма операции"] > 0])
    assert result == {"total_amount": 1000, "main": [{"category": "Зарплата", "amount": 1000}]}


@patch("views.get_user_currencies", return_value=["USD", "EUR", "BAD"])
@patch("views.requests.get")
def test_get_currency_rates(mock_get: Mock, _mock_currencies: Mock) -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"rates": {"USD": 0.011, "EUR": 0.01}}
    mock_get.return_value = response

    rates = get_currency_rates()
    assert rates == [{"currency": "USD", "rate": 0.01}, {"currency": "EUR", "rate": 0.01}]


@patch("views.get_user_stocks", return_value=["AAPL", "MSFT"])
@patch("views.requests.get")
def test_get_stock_prices(mock_get: Mock, _mock_stocks: Mock) -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"results": {"p": 186.324}}
    mock_get.return_value = response

    prices = get_stock_prices()
    assert prices == [{"stock": "AAPL", "price": 186.32}, {"stock": "MSFT", "price": 186.32}]


@patch("views.get_stock_prices", return_value=[{"stock": "AAPL", "price": 100.0}])
@patch("views.get_currency_rates", return_value=[{"currency": "USD", "rate": 0.01}])
@patch("views.calculate_period")
@patch("views.load_excel_data")
def test_get_events_data(
    mock_load_excel: Mock,
    mock_calculate_period: Mock,
    _mock_rates: Mock,
    _mock_stocks: Mock,
    operations_df: pd.DataFrame,
) -> None:
    mock_load_excel.return_value = operations_df
    mock_calculate_period.return_value = (
        pd.Timestamp("2026-02-01"),
        pd.Timestamp("2026-02-28"),
    )

    payload = get_events_data("10.02.2026")
    assert "expenses" in payload
    assert "income" in payload
    assert payload["currency_rates"] == [{"currency": "USD", "rate": 0.01}]
