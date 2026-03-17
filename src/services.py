from __future__ import annotations # включает отложенное разрешение аннотаций типов

import logging # Логирование программы
import math # Мат фун-ции(для округления вверх, округление limit)
import os # Формирование пути к файлу
from datetime import datetime, timedelta # Работа с датами и временными интервалами
from functools import reduce # Из модуля фун-ция reduce(преобразование Series в словарь)
from typing import Any, Dict, List, Tuple # Аннотация типов

import pandas as pd # Работа с табличными данными
from dotenv import load_dotenv # Библиотека, загрузка переменных из окружения .env

load_dotenv() # Загрузка переменных окружения из файла в текущую среду
logging.basicConfig(level=logging.INFO) # Настройка на вывод сообщений

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
def calculate_period(date_str: str, period: str = "M") -> Tuple[datetime, datetime]:
    """
    Рассчитывает начало и конец периода для заданной даты и типа периода.
    Поддерживаемые периоды: 'M' (месяц), 'W' (неделя), 'Y' (год), 'ALL' (все данные до даты).
    """
    # Преобразует строку date_str в объект datetime с помощью формата %d.%m.%Y (день.месяц.год)
    try:
        date = datetime.strptime(date_str, '%d.%m.%Y' # Преобразование строки в объект datetime

        if period == "W": # Начало-понедельник
            start_date = date - timedelta(days=date.weekday())
            end_date = date  # по ТЗ: диапазон "по входящую дату"
        elif period == "M":
            start_date = date.replace(day=1)
            end_date = date  # По заданию: с начала месяца по входящую дату
        elif period == "Y":
            start_date = date.replace(month=1, day=1)
            end_date = date
        elif period == "ALL":
            start_date = datetime.min
            end_date = date
        else:
            raise ValueError("Неверный период. Поддерживаются: W, M, Y, ALL")

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
def analyze_cashback_categories(data: pd.DataFrame, year: int, month: int) -> Dict[str, int]:
    """
    Анализирует кешбэк по категориям за указанный месяц и год.
    """
    try:
        logging.info(f'Начинаем анализ категорий за {year}-{month}')

        cashback_col_candidates = ["Кешбэк", "Кэшбэк", "кешбэк", "кэшбэк"] # ищет столбец с разными вариантами написания
        cashback_col = next((c for c in cashback_col_candidates if c in data.columns), None)
        if cashback_col is None:
            logging.warning("Колонка кешбэка не найдена; возвращаем пустой результат")
            return {}
# Фильтрует данные по году, месяцу, отрицательным суммам(расходы)
        filtered = (
            data.loc[
                (data["Дата операции"].dt.year == year)
                & (data["Дата операции"].dt.month == month)
                & (data["Сумма операции"] < 0)
            ]
            .copy()
        )

# Группирует по категориям, суммирует % кэшбэка, заменяет пропуски на 0, округляет до целых
        # функциональный стиль: transform -> groupby -> agg
        grouped = (
            filtered.groupby("Категория")[cashback_col]
            .sum(min_count=1)
            .fillna(0) # заменяет None на 0, чтобы корректно посчитать сумму
            .map(lambda x: int(round(float(x))))
        )
# Преобразует Series(результат группировки) в словарь{категория: сумма}
# acc-аккумулятор(промежуточный результат, словарь
# kv-пара ключ-значение из grouped.items(Продукты,150)
# {**acc}-распаковывает текущий аккумулятор и добавляет новую пару
# str(kv[0])- ключ(название категории),преобразуется в строку
# int(kv[1])-значение(сумма кэшбэка), преобразуется в целое число
# grouped.items() - второй аргумент(итератора пар из серии grouped)
# {} - третий аргумент(начальное значение аккумулятора: пустой словарь)

        result: Dict[str, int] = reduce(
            lambda acc, kv: {**acc, str(kv[0]): int(kv[1])},
            grouped.items(),
            {},
        )

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

        if limit <= 0:
            raise ValueError("limit должен быть положительным числом")
# Преобразование строки в формат ГГГГ-ММ
# .date() — извлекает дату (без времени)
# .replace(day=1) — устанавливает день месяца = 1. Получается первое число целевого месяца
        target_month = pd.to_datetime(month, format="%Y-%m").date().replace(day=1)
# Функция‑фильтр: проверяет, относится ли транзакция t к целевому месяцу
# Извлекает дату из транзакции, устанавливает день = 1 и сравнивает с target_month
        def is_target_month(t: Dict[str, Any]) -> bool:
            d = pd.to_datetime(t["Дата операции"]).date()
            return d.replace(day=1) == target_month
# Проверяет, является ли транзакция расходом (отрицательная сумма)
        def is_expense(t: Dict[str, Any]) -> bool:
            return float(t["Сумма операции"]) < 0
# Берёт модуль суммы транзакции (abs) — делает её положительной
# Делит на limit, округляет вверх (math.ceil) и умножает на limit — получает ближайшее кратное limit
# Вычитает исходную сумму — получает «отложенную» в копилку сумму
        def round_diff(t: Dict[str, Any]) -> float:
            amount = abs(float(t["Сумма операции"]))
            rounded = math.ceil(amount / limit) * limit
            return rounded - amount
# filter(is_target_month, transactions) — оставляет только транзакции целевого месяца
# filter(is_expense, ...) — из них оставляет только расходы
# map(round_diff, ...) — для каждой вычисляет разницу между
        total = sum(map(round_diff, filter(is_expense, filter(is_target_month, transactions))))

        logging.info(f'Расчёт для месяца {month}: итого {round(total, 2)}')
        return round(total, 2)
    except Exception as e:
        logging.error(f'Ошибка при расчёте инвесткопилки: {str(e)}')
        raise
