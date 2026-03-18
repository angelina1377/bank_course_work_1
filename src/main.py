import json
import sys # Импортируем модуль для работы с аргументами командной строки
from views import get_events_data # Импортируем функцию для загрузки Excel
from utils import validate_date # Импортируем функцию валидацию даты

def main():
    # Проверяем кол-во аргументов командной строки
    if len(sys.argv) < 2:
        print("Использование: python mail.py дата [период]")
        sys.exist(1) # Завершаем программу с кодом ошибки

    # Получаем дату из аргументов
    date_str = sys.argv[1]

    # Получаем период(по умолчанию "М" - месяц)
    period = sys.argv[2] if len(sys.argv) > 2 else 'M'

    # Валидируем дату
    if not validate_date(date_str):
        print("Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        sys.exit(1) # Завершаем программу при ошибке

    try:
        # Получаем данные событий
        result= get_events_data(date_str, period)

    # Выводим результат в формате JSON
    print(json.dumps(
        result,
        ensure_ascii= False, # Разрешаем вывод не-ASCII символов
        indent = 2 # Форматируем JSON с отступами
    ))

    except Exception as e:
    # Обрабатываем возможные ошибки
       print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__"
    main() # Запускаем основную функцию при прямом запуске скрипта