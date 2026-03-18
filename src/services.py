import pandas as pd # Библиотека для работы с данными (DataFrame)
from datetime import datetime, timedelta # Для работы с датами и временными интервалами
import os # Для работы с операционной системой
from dotenv import load_dotenv # Для работы с переменными окружения из .env файла
import logging # Для логирования действий программы
from typing import List, Dict, Any # Для типизации

load_dotenv() # Загружаем переменные окружения из .env файла
logging.basicConfig(level=logging.INFO)# Устанавливаем уровень логирования INFO

# Функция загрузки данных:
def load_excel_data() -> pd.DataFrame:
    try:
        file_path = os.path.join('data', 'operations.xlsx') # папка data + файл operations.xlsx
        logging.info(f'Загружаем данные из {file_path}') # Записывает в лог информационное сообщение о начале загрузки данных
        df = pd.read_excel(file_path) # Читает Excel‑файл по указанному пути и сохраняет данные в DataFrame df
        df['Дата операции'] = pd.to_datetime(df['Дата операции']) # Преобразует столбец Дата операции из строкового формата в тип datetime
        # Нужно для фильтрации по датам и расчётов периодов
        return df # Возвращает загруженный DataFrame
    except Exception as e:
        logging.error(f'Ошибка при загрузке данных: {str(e)}')
        raise

# Функция расчета периода
def calculate_period(date_str: str, period: str = 'M') -> tuple:
    """
    Рассчитывает начало и конец периода для заданной даты и типа периода.
    Поддерживаемые периоды: 'M' (месяц), 'W' (неделя), 'Y' (год), 'ALL' (все данные до даты).
    """
    # Преобразует строку date_str в объект datetime с помощью формата %d.%m.%Y (день.месяц.год)
    try:
        date = datetime.strptime(date_str, '%d.%m.%Y')

        if period == 'W':
            start_date = date - timedelta(days=date.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'M':
            start_date = date.replace(day=1)
            end_date = date  # По заданию: с начала месяца по входящую дату
        elif period == 'Y':
            start_date = date.replace(month=1, day=1)
            end_date = date
        elif period == 'ALL':
            start_date = datetime.min
            end_date = date
        else:
            raise ValueError('Неверный период. Поддерживаются: W, M, Y, ALL')

        return start_date, end_date
    except Exception as e:
        logging.error(f'Ошибка при расчёте периода: {str(e)}')
        raise

# Функция фильтрации транзакций
# Фильтрует DataFrame df по конкретной дате date
def get_transactions_by_date(df: pd.DataFrame, date: datetime) -> pd.DataFrame:
    try:
        logging.info(f'Фильтруем транзакции по дате: {date}')
        # Возвращает DataFrame с транзакциями за этот день
        # Отбирает строки, где дата в столбце Дата операции совпадает с переданной датой date
        return df[df['Дата операции'].dt.date == date.date()]
    except Exception as e:
        logging.error(f'Ошибка при фильтрации по дате: {str(e)}')
        raise

# Функция анализа кэшбэка за указанный год и месяц
def analyze_cashback_categories(data: pd.DataFrame, year: int, month: int) -> Dict[str, float]:
    """
    Анализирует кешбэк по категориям за указанный месяц и год.
    """
    try:
        logging.info(f'Начинаем анализ категорий за {year}-{month}')

        # Фильтруем данные по году, месяцу и отрицательным суммам (расходы)
        filtered_data = data[
            (data['Дата операции'].dt.year == year) &
            (data['Дата операции'].dt.month == month) &
            (data['Сумма операции'] < 0)
        ]

        # Группируем по категориям и считаем суммы кешбэка (учитываем модуль суммы)
        category_sums = filtered_data.groupby('Категория').apply(
            lambda x: (abs(x['Сумма операции']) * x['кэшбек'] / 100).sum()
        ).to_dict()

        # Преобразуем в нужный формат (округляем до целых чисел)
        result = {category: round(amount) for category, amount in category_sums.items()}

        logging.info(f'Анализ завершён. Результат: {result}')
        return result
    except Exception as e:
        logging.error(f'Ошибка при анализе категорий: {str(e)}')
        raise

# Функция расчета инвестиций банка
def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму для инвесткопилки через округление трат.
    """
    try:
        if not transactions:
            logging.warning('Список транзакций пуст')
            return 0.0

        total = 0.0
        target_month = pd.to_datetime(month).date().replace(day=1)

        for transaction in transactions:
            transaction_date = pd.to_datetime(transaction['Дата операции']).date()
            # Проверяем, что транзакция относится к нужному месяцу
            if transaction_date.replace(day=1) != target_month:
                continue

            amount = transaction['Сумма операции']
            # Учитываем только расходы (отрицательные суммы)
            if amount >= 0:
                continue

            # Округление вверх до ближайшего кратного limit (для положительных чисел)
            positive_amount = abs(amount) # Преобразует сумму транзакции в положительное число
            rounded = ((positive_amount + limit - 1) // limit) * limit
            total += rounded - positive_amount

        logging.info(f'Расчёт для месяца {month}: итого {round(total, 2)}')
        return round(total, 2)
    except Exception as e:
        logging.error(f'Ошибка при расчёте инвесткопилки: {str(e)}')
        raise
