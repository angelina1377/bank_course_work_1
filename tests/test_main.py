import json
from unittest.mock import patch

from main import main


@patch("main.get_events_data", return_value={"status": "ok"})
@patch("main.validate_date", return_value=True)
@patch("main.sys.argv", ["main.py", "01.02.2026", "M"])
def test_main_success(_mock_validate, _mock_events, capsys) -> None:
    code = main()
    captured = capsys.readouterr()
    assert code == 0
    assert json.loads(captured.out) == {"status": "ok"}


@patch("main.sys.argv", ["main.py"])
def test_main_no_args(capsys) -> None:
    code = main()
    captured = capsys.readouterr()
    assert code == 1
    assert "Использование" in captured.out
