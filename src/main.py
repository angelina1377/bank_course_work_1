import json # работа с JSON‑файлами
import sys # получение параметров, переданных при запуске скрипта (sys.argv)

from src.utils import validate_date
from src.views import get_events_data

# точка входа в программу. Выполняет основную логику скрипта
def main() -> None:
#  проверяет, переданы ли обязательные аргументы при запуске
    if len(sys.argv) < 2: # получает количество аргументов командной строки
        print("Использование: python -m src.main ДД.ММ.ГГГГ [W|M|Y|ALL]")
        sys.exit(1) # завершает программу с кодом ошибки 1 (неуспешное завершение)

    date_str = sys.argv[1] # берёт первый аргумент (sys.argv[1]) как строку с датой)
# period — берёт второй аргумент (sys.argv[2]), если он есть
# Если нет — устанавливает значение по умолчанию "M" (месяц)
    period = sys.argv[2] if len(sys.argv) > 2 else "M"
# проверяет корректность формата даты
    if not validate_date(date_str):
        print("Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        sys.exit(1) # Завершает программу с кодом 1
# Основной блок выполнения
    try:
        result = get_events_data(date_str, period)# получает данные за указанный период
        print(json.dumps(result, ensure_ascii=False, indent=2))# преобразует результат в строку JSON
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()