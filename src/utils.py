from __future__ import annotations # # включает отложенное разрешение аннотаций типов

import logging # Логирование программы
from datetime import datetime # Работа с датами
from typing import Optional # Аннотация типов

import pandas as pd  # Работа с табличными данными

# Настройка логирования:

logging.basicConfig(

    level=logging.INFO,  # Устанавливаем уровень логирования INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат вывода логов
)
# Функция валидации даты: проверяет, является ли строка корректной датой
def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except (TypeError, ValueError):
        return False

# Функция конвертации суммы: округляет число с плавающей точкой до целого
def convert_amount(amount: float) -> int:
    return round(amount)

# Функция получения текущей даты: возвращает текущую дату в формате ДД.ММ.ГГГГ
def get_current_date():
    return datetime.now().strftime("%d.%m.%Y")

# Функция фильтрации транзакций: фильтрует DataFrame с транзакциями по диапазону дат
def filter_transactions(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    *,
    date_column: str = "Дата операции",
) -> pd.DataFrame:
    return df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]

# Функция подсчета общей суммы: считает сумму по столбцу "Сумма операции" и округляет результат
def calculate_total(df):
    return round(df["Сумма операции"].sum())

# Функция парсинга даты: преобразует строку с датой в объект datetime. Если строка None, возвращает None
def parse_date(date_str: Optional[str], fmt: str = "%d.%m.%Y") -> Optional[datetime]:
    if date_str is None:
        return None
    return datetime.strptime(date_str, fmt)