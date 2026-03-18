import pandas as pd # Для работы с данными
import json # Для работы с JSON
from datetime import datetime # Для работы с датами
import requests # Для HTTP-запросов
from dotenv import load_dotenv # Для работы с переменными окружения
import os # Для работы с операционной системой
from services import load_excel_data, calculate_period # Импортируем функции из services.py
import logging # Для логирования действий программы

load_dotenv() # Загружаем переменные окружения из .env файла

# Функции работы с настройками пользователя
# Кешируем чтение настроек пользователя(избегает повторного чтения файла при каждом вызове)
def get_user_settings():
    if not hasattr(get_user_settings, 'cache'): # Проверяет, есть ли у функции атрибут cache (был ли файл уже прочитан)
        with open('user_settings.json') as f: # Если нет — открывает файл и сохраняет его содержимое
            get_user_settings.cache = json.load(f)
    return get_user_settings.cache

# Функция работы с настройками пользователя
def get_user_currencies():
    """Получаем список валют пользователя из настроек"""
    settings = get_user_settings()
    return settings.get('user_currencies', [])
# берёт значение по ключу user_currencies, если ключа нет — возвращает пустой список

def get_user_stocks():
    """Получаем список акций пользователя из настроек"""
    settings = get_user_settings()
    return settings.get('user_stocks', [])

# Функции работы с API
def get_currency_rates():
    """Получаем актуальные курсы валют"""
    api_key = os.getenv('CURRENCY_API_KEY')
    url = f'https://api.exchangerate-api.com/v4/latest/RUB'
    try:
        response = requests.get(url) # Делаем get запрос
        response.raise_for_status() # Проверяем успешность запроса
        data = response.json() # Парсим ответ в json
        rates = [] # Создаем пустой список для курсов
        # Проходим по всем валютам из настроек пользователя
        for currency in get_user_currencies():
            try:
                rates.append({
                    "currency": currency,
            "rate": round(data['rates'][currency], 2)
        })
            except KeyError:
                logging.warning(f"Валюта {currency} не найдена в ответе API")
        return rates
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении курсов валют: {e}")
        return []

def get_stock_prices():
    api_key = os.getenv('STOCK_API_KEY') # Получаем API ключ
    base_url = 'https://api.polygon.io/v2/last/stock/'  # Базовый URL
    prices = []
    try:
        for stock in get_user_stocks(): # Прохожим по все акциям пользователя
            response = requests.get(
                f"{base_url}{stock}/quotes",
                params={'apiKey': api_key}
            )
            response.raise_for_status()
            data = response.json()
            try:
                prices.append({
            "stock": stock,
            "price": round(data['last']['price'], 2)
        })
            except KeyError:
                logging.warning(f"Не удалось получить цену для акции {stock}")
        return prices
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении цен акций: {e}")
        return []

# Функция обработки транзакций
def process_expenses(df):
    total_amount = round(df['Сумма операции'].sum() * -1) # умножаем на -1, чтобы получить положительное число
    # Группируем расходы по категориям
    category_groups = df.groupby('Категория')['Сумма операции'].sum().apply(lambda x: round(x * -1))
    # Берем 7 основных категорий
    main_categories = category_groups.nlargest(7).to_dict()
    # Если категорий больше 7, создаем категорию "Остальное"
    if len(main_categories) > 7:
        # Получаем все категории, которых нет в main_categories
        other_categories = category_groups.drop(main_categories.keys())
        # Суммируем их значения
        rest_amount = other_categories.sum()
        main_categories["Остальное"] = round(rest_amount)
    # Формируем список основных категорий
    main = [{"category": cat, "amount": amount} for cat, amount in main_categories.items()]
    # Фильтруем переводы и наличные
    transfers_cash = df[df['Категория'].isin(['Наличные', 'Переводы'])]
    transfers_cash_groups = transfers_cash.groupby('Категория')['Сумма операции'].sum().apply(
        lambda x: round(x * -1)
    ).to_dict()
    # Формируем список переводов и наличных
    transfers_and_cash = [{"category": cat, "amount": amount} for cat, amount in transfers_cash_groups.items()]
    return {
        "total_amount": total_amount,
        "main": main,
        "transfers_and_cash": transfers_and_cash
    }

# Функция обработки доходов
def process_income(df):
    total_amount = round(df["Сумма операции"].sum())
    # Группируем доходы по категориям
    category_groups = df.groupby("Категория")['Сумма операции'].sum().apply(lambda x: round(x))
    # Берем 3 основные категории доходов
    main_categories = category_groups.nlargest(3).to_dict()
    # Формируем список основных категорий
    main = [{"category": cat, "amount": amount} for cat, amount in main_categories.items()]
    return {
        "total_amount": total_amount,
        "main": main
    }

# Функция получения данных по событиям
def get_events_data(date_str, period='M'):
    df = load_excel_data() # Загружаем данные из Excel
    start_date, end_date = calculate_period(date_str, period) # Рассчитываем период
    # Фильтруем данные по дате
    filtered_df = df[(df['Дата операции'] >= start_date) & (df['Дата операция'] <= end_date)]
    # Разделяем на расходы и доходы
    expenses_df = filtered_df[filtered_df['Сумма операции'] < 0]
    income_df = filtered_df[filtered_df['Сумма операции'] > 0]
    return {
        "expenses": process_expenses(expenses_df),
        "income": process_income(income_df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices()
    }
