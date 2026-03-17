import pandas as pd

from src.reports import report_decorator, spending_by_category


def test_spending_by_category_computes_90d_spending():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2020-05-01", "2020-05-02", "2020-05-03"]),
            "Категория": ["Food", "Food", "Other"],
            "Сумма операции": [-100, -50, -999],
        }
    )
    out = spending_by_category(df, "Food", date="2020-05-10")
    assert out.loc[0, "Категория"] == "Food"
    assert out.loc[0, "Траты"] == 150


def test_report_decorator_writes_dataframe_json(tmp_path):
    out_file = tmp_path / "out.json"

    @report_decorator(str(out_file))
    def make_report() -> pd.DataFrame:
        return pd.DataFrame({"a": [1, 2]})

    df = make_report()
    assert df["a"].tolist() == [1, 2]
    assert out_file.exists()
