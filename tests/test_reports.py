from datetime import datetime
import json

import pandas as pd

from reports import report_decorator, spending_by_category, weekly_spending_report, work_weekend_report


def _transactions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2026-01-10", "2026-01-11", "2026-02-01"]),
            "Сумма операции": [-100, -200, -50],
            "Категория": ["Еда", "Еда", "Транспорт"],
        }
    )


def test_spending_by_category() -> None:
    report_fn = spending_by_category.__wrapped__
    result = report_fn(_transactions(), "Еда", datetime(2026, 2, 1))

    assert int(result.iloc[0]["Общие траты"]) == 300


def test_weekly_spending_report() -> None:
    result = weekly_spending_report.__wrapped__(_transactions(), datetime(2026, 2, 1))
    assert not result.empty


def test_work_weekend_report() -> None:
    result = work_weekend_report.__wrapped__(_transactions(), datetime(2026, 2, 1))
    assert list(result["Тип дня"]) == ["Рабочие дни", "Выходные"]


def test_report_decorator_writes_file(tmp_path) -> None:
    path = tmp_path / "out.json"

    @report_decorator(str(path))
    def fake_report() -> pd.DataFrame:
        return pd.DataFrame({"x": [1]})

    fake_report()
    assert json.loads(path.read_text(encoding="utf-8")) == [{"x": 1}]
