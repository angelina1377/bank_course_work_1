from  datetime import datetime  # Импортируем работу с датами
import pandas as pd  # Импортируем библиотеку для работы с данными
import logging

# Настройка логирования:

logging.basicConfig(

    level=logging.INFO,  # Устанавливаем уровень логирования INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат вывода логов
)
# Функция валидации даты
def validate_date(date_str):
     try:
         datetime.strpttime(date_str,'%d.%m.%Y') # Пытаемся преобразовать строку в дату
         return  True # Если успешно, возвращаем True

     except ValueError:
         return  False # Если ошибка, возвращаем False

# Функция конвертации суммы
def convert_amount(amount):
    return round(amount) # Округляет сумму до целого числа

# Функция получения текущей даты
def get_current_date():
    return datetime.now().strptime('%d.%m.%Y') # Возвращает текущую дату в формате ДД.ММ.ГГГГ

# Функция фильтрации транзакций
def filter_transactions(sf, start_date, end_date):
    return df[
        (df['Дата операции'] >= start_date) & # фильтрация по дате начала
        (df['Дата операции'] <= end_date) # Фильтрации по дате конца
    ]

# Функция подсчета общей суммы
def calculate_total(df):
    return round(df['Сумма операции'].sum()) # Суммирует все значения в колонке "Сумма операции" и округляет