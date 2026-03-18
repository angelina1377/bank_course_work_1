import  pandas as pd  # Для работы с DataFrame
from datetime import datetime, timedelta  # Для работы с датами
from typing import Optional # Для типизации опциональных параметров
import json  # Для работы с JSON
from functools import wraps  # Для создания декораторов
from typing import Dict  # Для типизации

# Декоратор report_decorator

def report_decorator(filename: str = "report.json"):
    def decorator(func): # Внутренняя фун-ция, принимающая декорируемую функцию
        @wraps(func) # Сохраняет имя, документацию исходной фун-ции
        def wrapper(*args, **kwargs): # Обертка, которая перехватывает аргументы функции
            result = func(*args, **kwargs) # Выполняем исходную функ-цию и получает результат
            # Преобразуем DataFrame в словарь для JSON
            with open(filename, 'w', encoding='utf-8') as f: # Открывает файл для записи
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            return result
        return wrapper
    return decorator

@report_decorator()  # Без параметра — файл по умолчанию
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[datetime] = None) -> pd.DataFrame:
    if date is None:
        date = datetime.now()
 # Расчет периода
    end_date = date
    start_date = end_date - timedelta(days=90)

    # Фильтрация данных (оставляет только транзакции за последние 3 месяца по заданной категории
    filtered_df = transactions[
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date) &
        (transactions['Категория'] == category)
    ]

    result_df = pd.DataFrame({
        'Категория': [category],
        'Общие траты': [round(filtered_df['Сумма операции'].sum() * -1)],
        'Период': [f'{start_date.date()} - {end_date.date()}']
    })
    return result_df

@report_decorator("weekly_report.json")  # С параметром — кастомное имя файла
def weekly_spending_report(transactions: pd.DataFrame,
                           date: Optional[datetime] = None) -> pd.DataFrame:
    if date is None:
        date = datetime.now()

    end_date = date
    start_date = end_date - timedelta(days=90)

    filtered_df = transactions[
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date)
    ]
# Группировка по дням недели, суммирование, округление
    weekly_spending = filtered_df.groupby(
        filtered_df['Дата операции'].dt.day_name()
    )['Сумма операции'].sum().apply(lambda x: round(x * -1)).reset_index()
    return weekly_spending

@report_decorator("work_weekend_report.json")
def work_weekend_report(transactions: pd.DataFrame,
                        date: Optional[datetime] = None) -> pd.DataFrame:
    if date is None:
        date = datetime.now()

    end_date = date
    start_date = end_date - timedelta(days=90)

    filtered_df = transactions[
        (transactions['Дата операции'] >= start_date) &
        (transactions['Дата операции'] <= end_date)
    ]
# dt.weekday - возвращает номер дня недели
    filtered_df['IsWeekend'] = filtered_df['Дата операции'].dt.weekday >= 5
# Разделение трат
    work_spending = filtered_df[~filtered_df['IsWeekend']]['Сумма операции'].sum() * -1
    weekend_spending = filtered_df[filtered_df['IsWeekend']]['Сумма операции'].sum() * -1

    result_df = pd.DataFrame({
        'Тип дня': ['Рабочие дни', 'Выходные'],
        'Общие траты': [round(work_spending), round(weekend_spending)]
    })
    return result_df