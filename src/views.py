from __future__ import annotations # включает отложенное разрешение аннотаций типов
import json # работа с JSON‑файлами
import logging # Логирование программы
import os # Формирование пути к файлу
from typing import Any, Dict, List # аннотации типов

# Функции работы с настройками пользователя
# Кешируем чтение настроек пользователя(избегает повторного чтения файла при каждом вызове)
def get_user_settings():
    if not hasattr(get_user_settings, 'cache'): # Проверяет, есть ли у функции атрибут cache (был ли файл уже прочитан)
        with open('user_settings.json') as f: # Если нет — открывает файл и сохраняет его содержимое
            get_user_settings.cache = json.load(f)
    return get_user_settings.cache

# возвращает список валют пользователя из настроек
def get_user_currencies() -> List[str]:
    settings = get_user_settings() # Берем значение по данному ключу(валюта)
    return list(settings.get("user_currencies", [])) # Если ключа нет, возвращаем пустой список

# возвращает список акций пользователя
def get_user_stocks() -> List[str]:
    settings = get_user_settings() # Берем значение по данному ключу(акции)
    return list(settings.get("user_stocks", [])) # Если ключа нет, возвращаем пустой список

# Функции получения данных из API
def get_currency_rates() -> List[Dict[str, Any]]:
    url = "https://api.exchangerate-api.com/v4/latest/RUB"
    try:
        response = requests.get(url, timeout=10) # Выполняет GET‑запрос с таймаутом 10 секунд
        response.raise_for_status() # Проверяет статус ответа(выбрасывает исключение при ошибке HTTP)
        data = response.json() # Парсит JSON‑ответ от API
        # проверяет, есть ли курс в ответе API, округляет, добавляет в список, при ошибке записывает в лог
        rates_by_code = data.get("rates", {}) if isinstance(data, dict) else {}

        result: List[Dict[str, Any]] = []
        for code in get_user_currencies():
            if code in rates_by_code:
                result.append({"currency": code, "rate": round(float(rates_by_code[code]), 2)})
            else:
                logger.warning("Валюта %s не найдена в ответе API", code)
        return result
    except requests.RequestException as e:
        logger.error("Ошибка при получении курсов валют: %s", e)
        return []

# получает цены акций для акций пользователя через API
def get_stock_prices() -> List[Dict[str, Any]]:
    api_key = os.getenv("STOCK_API_KEY") # Берёт API‑ключ из переменных окружения
    base_url = "https://api.polygon.io/v2/last/stock/"

    if not api_key:
        logger.warning("Не задан STOCK_API_KEY; цены акций будут пустыми")
        return []

    prices: List[Dict[str, Any]] = []
    try:
        for ticker in get_user_stocks():
            response = requests.get(
                f"{base_url}{ticker}/quotes",
                params={"apiKey": api_key},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            try:
                price = float(data["last"]["price"])
            except Exception:
                logger.warning("Не удалось получить цену для акции %s", ticker)
                continue
            prices.append({"stock": ticker, "price": round(price, 2)})
        return prices
    except requests.RequestException as e:
        logger.error("Ошибка при получении цен акций: %s", e)
        return []

# преобразует Series (результат группировки) в отсортированный список словарей
def _series_to_sorted_items(series: pd.Series) -> List[Dict[str, Any]]:
    if series.empty:
        return []
    sorted_series = series.sort_values(ascending=False)
    return [{"category": str(k), "amount": int(v)} for k, v in sorted_series.items()]

# анализирует расходы из DataFrame, группирует по категориям, выделяет топ‑7 и отдельно обрабатывает переводы/наличные
def process_expenses(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"total": 0, "main": [], "transfers_and_cash": []}

    expenses = df[df["Сумма операции"] < 0].copy() # фильтрует DataFrame — оставляет только строки с отрицательными суммами (расходы)
 # считает общую сумму расходов                                                 # .copy() — создаёт независимую копию, чтобы не изменять исходный DataFrame
    total = int(round((-expenses["Сумма операции"]).sum()))
# группирует расходы по категориям и сортирует по убыванию
    by_category = (-expenses.groupby("Категория")["Сумма операции"].sum()).round().astype(int)
    by_category = by_category.sort_values(ascending=False)
# выделяет топ‑7 категорий и сумму по всем остальным
    top7 = by_category.head(7)
    rest_sum = int(by_category.iloc[7:].sum()) if len(by_category) > 7 else 0
# преобразует топ‑7 в список словарей и добавляет категорию «Остальное», если есть мелкие траты
    main_items = _series_to_sorted_items(top7)
    if rest_sum:
        main_items.append({"category": "Остальное", "amount": int(rest_sum)})
# отдельно анализирует траты по категориям «Наличные» и «Переводы»
    transfers_cash = expenses[expenses["Категория"].isin(["Наличные", "Переводы"])]
    by_tc = (-transfers_cash.groupby("Категория")["Сумма операции"].sum()).round().astype(int)
    transfers_and_cash = _series_to_sorted_items(by_tc)

    return {"total": total, "main": main_items, "transfers_and_cash": transfers_and_cash}

# аналогично process_expenses, но для доходов (положительные суммы)
def process_income(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"total": 0, "main": []}

    income = df[df["Сумма операции"] > 0].copy()
    total = int(round(income["Сумма операции"].sum()))
    by_category = income.groupby("Категория")["Сумма операции"].sum().round().astype(int)
    main_items = _series_to_sorted_items(by_category)
    return {"total": total, "main": main_items}

# собирает все данные за указанный период: расходы, доходы, курсы валют, цены акций
def get_events_data(date_str: str, period: str = "M") -> Dict[str, Any]:
    df = load_excel_data()
    start_date, end_date = calculate_period(date_str, period)

    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    return {
        "expenses": process_expenses(filtered_df),
        "income": process_income(filtered_df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }
