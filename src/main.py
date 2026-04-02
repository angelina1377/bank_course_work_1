
from __future__ import annotations

import json
import sys

from utils import validate_date
from views import get_events_data


def main() -> int:
    """Проверяем кол-во аргументов командной строки."""
    if len(sys.argv) < 2:
        print("Использование: python src/main.py <дата> [период]")
        return 1

    date_str = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else "M"

    if not validate_date(date_str):
        print("Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        return 1

    try:
        result = get_events_data(date_str, period)
    except Exception as exc:  # pragma: no cover
        print(f"Произошла ошибка: {exc}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())