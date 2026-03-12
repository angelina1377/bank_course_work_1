# Импорт библиотек
import pandas as pd #Библиотека для работы с данными (DataFrame)
from datetime import datetime, timedelta # Для работы с датами и временными интервалами
import os # Для работы с файловой системой
from dotenv import load_dotenv # Для работы с переменными окружения из .env файла
import logging # Для логирования действий
from typing import List, Dict, Any # Для типизации

load_dotenv() # Загружаем переменные окружения из .env файла

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция загрузки данных:
def load_excel_data() -> pd.DataFrame:
    try:
        file_path = os.path.join('data', 'operations.xlsx') # Формируем путь к файлу Excel
        logging.info(f'Загружаем данные из {file_path}') # Записываем в лог
        df = pd.read_excel(file_path) # Читаем Excel файл в DataFrame
        df['Дата операции'] = pd.to_datetime(df['Дата операции']) # Преобразуем даты в формат datetime
        return df # Возвращаем DataFrame

    except Exception as e:
        logging.error(f'Ошибка при загрузке данных:{str(e)}') # Логируем ошибку
        raise # Перебрасываем исключение

# Функция расчета периода:
def calculate_period(date_str: str, period: str  = 'M') -> tuple: # date_str — входная строка с датой (например, '25.12.2025')
    try:
        date = datetime.strptime(date_str, '%d.%m.%Y') # Преобразуем строку в дату

        if period == 'W': # Если период-неделя
            start_date = date - timedelta(days=date.weekday()) # Начало недели date.weekday() возвращает номер дня недели
            # (понедельник = 0, воскресенье = 6)
            end_date = start_date + timedelta(days=6) # Конец недели
            # прибавляет 6 дней к понедельнику, получая воскресенье — конец недели

        elif period == 'M': # Если период-месяц
            start_date = date.replace(day=1) # заменяет день в дате на 1,
            # оставляя месяц и год — получаем первое число месяца
            end_date = (start_date + pd.offsets.MonthEnd(1)) - timedelta(days=1) # Последнее число месяца
            # pd.offsets.MonthEnd(1) — функция из библиотеки pandas, которая сдвигает дату на конец месяца;
            # вычитание timedelta(days=1) нужно, потому что MonthEnd может давать дату следующего месяца
            # мы возвращаем её на один день назад, получая последний день текущего месяца

        elif period == 'Y': # Если период-год
            start_date = date.replace(month=1, day=1) # 1 января
            end_date = date.replace(month=12, day=31) # 31 декабря

        elif period == 'ALL': # Если весь период
            start_date = datetime.min # Самая ранняя возможная дата
            end_date = date # Текущая дата(входная дата)

        else:
            raise ValueError('Неверный период') # Ошибка при неверном периоде

        return start_date, end_date # Возвращаем даты начала и конца периода

    except Exception as e:
        logging.error(f'Ошибка при расчете периода: {str(e)}') # Логируем ошибку
        raise # Перебрасываем исключение

# Функция фильтрация транзакций:
def get_transactions_by_date(df:pd.DataFrame, date:datetime) -> pd.DataFrame:
    try:
        logging.info (f'Фильтруем транзакции по дате: {date}') # Логируем начало операции
        return df[df['Дата операции'].dt.date == date.date()] # Фильтруем DataFrame по дате (без времени)
    except Exception as e:
        logging.error(f'Ошибка при фильтрации по дате: {str(e)}') # Логируем ошибку
        raise # Перебрасываем исключение

# Функция анализа категорий кэшбэка
def analyze_cashback_categories(data:pd.DataFrame, year: int, month:int) -> Dict[str, float]
    try:
        logging.info(f'Начинаем анализ категорий за {year}-{month}') # Записываем в лог

        # Фильтруем данные по году и месяцу
        filtered_data = data[(data['Дата операции'].dt.year == year) &
                             (data['Дата операции'].dt.month == month)]

        # Группируем по категориям и считаем суммы кэшбэка
        category_sums = filtered_data.groupby('Категория').apply(
            lambda x: (x['Сумма операции'] * x['Кэшбэк] / 100).sum()'
                                               ).to_dict()

        # Преобразуем в нужный формат(округляем  до целых чисели берем модуль)
        result = {category: round(amount) for category, amount in category_sums.items()}

        # Логирование результата
        logging.info(f'Анализ завершен.Результат:{result}')
        return result

    except Exception as e:
        logging.info(f'Ошибка при анализе категорий:{str(e)}')# Логируем ошибку
        raise # Перебрасываем исключение

# Функция расчета инвестиций банка
def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    try:
        if not transactions: # Проверка входных данных
            logging.warning('Список транзакций пуст') # Если список пустой
            return 0.0 # Возвращаем 0

        total = 0
        target_month = pd.to_datetime(month).date().replace(day=1)

        for transaction in transactions:
            transaction_date = pd.to_datetime(transaction['Дата операции']).date()
            # Проверяем, что транзакции относится к нужному месяцу
            if transaction_date.replace(day=1) != target_month:
                continue

            amount = transaction['Сумма операции'] # Берем сумму операции
            rounded = ((amount + limit -1) // limit ) * limit # Округляем до ближайшего значения
            total += rounded - amount # Считаем разницу

            # Логирование результата
            logging.info(f'Расчет для месяца {month}: итого{round(total, 2)}')
            return round(total, 2) # Возвращаем итоговую сумму

    except Exception as e:
        logging.error(f'Ошибка при расчете инвесткопилки:{str(e)}') # Логируем ошибку
        raise # Перебрасываем исключение



