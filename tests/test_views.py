from datetime import datetime

import pandas as pd

from src import views


def test_process_expenses_top7_and_rest_and_transfers_cash():
    rows = []
    # 8 categories of expenses
    for i in range(8):
        rows.append(
            {
                "Дата операции": datetime(2020, 5, 1),
                "Сумма операции": -(100 + i),
                "Категория": f"C{i}",
            }
        )
    # add transfers & cash
    rows += [
        {"Дата операции": datetime(2020, 5, 2), "Сумма операции": -500, "Категория": "Переводы"},
        {"Дата операции": datetime(2020, 5, 3), "Сумма операции": -200, "Категория": "Наличные"},
    ]
    df = pd.DataFrame(rows)
    out = views.process_expenses(df)

    assert out["total"] == int(round((-df["Сумма операции"]).sum()))
    assert len([x for x in out["main"] if x["category"] != "Остальное"]) == 7
    assert any(x["category"] == "Остальное" for x in out["main"])

    tc = out["transfers_and_cash"]
    assert {x["category"] for x in tc} == {"Переводы", "Наличные"}
    assert tc[0]["amount"] >= tc[1]["amount"]  # sorted desc


def test_get_events_data_filters_and_integrates(monkeypatch):
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2020-05-01", "2020-05-21"]),
            "Сумма операции": [-10, -20],
            "Категория": ["A", "B"],
        }
    )

    monkeypatch.setattr(views, "load_excel_data", lambda: df)
    monkeypatch.setattr(views, "calculate_period", lambda date_str, period: (datetime(2020, 5, 1), datetime(2020, 5, 20)))
    monkeypatch.setattr(views, "get_currency_rates", lambda: [{"currency": "USD", "rate": 90.0}])
    monkeypatch.setattr(views, "get_stock_prices", lambda: [{"stock": "AAPL", "price": 100.0}])

    out = views.get_events_data("20.05.2020", "M")
    assert out["expenses"]["total"] == 10  # only first row in range
    assert out["currency_rates"][0]["currency"] == "USD"
    assert out["stock_prices"][0]["stock"] == "AAPL"
