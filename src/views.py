"""Помощники по подготовке интеграции."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from services import calculate_period, load_excel_data

LOGGER = logging.getLogger(__name__)

DATE_COLUMN = "Дата операции"
AMOUNT_COLUMN = "Сумма операции"
CATEGORY_COLUMN = "Категория"
SETTINGS_PATH = Path("user_settings.json")


def get_user_settings() -> dict[str, Any]:
    """Считывание и кэширование настроек из json."""
    if not hasattr(get_user_settings, "cache"):
        with SETTINGS_PATH.open(encoding="utf-8") as file_obj:
            get_user_settings.cache = json.load(file_obj)
    return get_user_settings.cache


def get_user_currencies() -> list[str]:
    """Возвращает валюты пользователя."""
    return list(get_user_settings().get("user_currencies", []))


def get_user_stocks() -> list[str]:
    """Возвращает акции пользователя."""
    return list(get_user_settings().get("user_stocks", []))


def get_currency_rates() -> list[dict[str, float | str]]:
    """Получаем актуальные курсы валют."""
    url = "https://api.exchangerate-api.com/v4/latest/RUB"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        rates_data = response.json().get("rates", {})
    except requests.RequestException as exc:
        LOGGER.error("Ошибка при получении курсов валют: %s", exc)
        return []

    rates: list[dict[str, float | str]] = []
    for currency in get_user_currencies():
        if currency not in rates_data:
            LOGGER.warning("Валюта %s не найдена в ответе API", currency)
            continue
        rates.append({"currency": currency, "rate": round(float(rates_data[currency]), 2)})
    return rates


def get_stock_prices() -> list[dict[str, float | str]]:
    """Получаем цены акций."""
    api_key = os.getenv("STOCK_API_KEY", "")
    base_url = "https://api.polygon.io/v2/last/stock"
    prices: list[dict[str, float | str]] = []

    for stock in get_user_stocks():
        try:
            response = requests.get(f"{base_url}/{stock}", params={"apiKey": api_key}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            LOGGER.error("Ошибка при получении цены акции %s: %s", stock, exc)
            continue

        price = data.get("results", {}).get("p")
        if price is None:
            LOGGER.warning("Не удалось получить цену для акции %s", stock)
            continue

        prices.append({"stock": stock, "price": round(float(price), 2)})
    return prices


def process_expenses(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Сводная статистика расходов в json."""
    if dataframe.empty:
        return {"total_amount": 0, "main": [], "transfers_and_cash": []}

    totals = (-dataframe.groupby(CATEGORY_COLUMN)[AMOUNT_COLUMN].sum()).round()
    top_categories = totals.nlargest(7)
    other_total = totals.drop(index=top_categories.index, errors="ignore").sum()

    main = [{"category": category, "amount": int(amount)} for category, amount in top_categories.items()]
    if other_total > 0:
        main.append({"category": "Остальное", "amount": int(round(other_total))})

    transfers = totals[totals.index.isin(["Наличные", "Переводы"])]
    transfers_and_cash = [
        {"category": category, "amount": int(amount)} for category, amount in transfers.items()
    ]
    return {"total_amount": int(round(-dataframe[AMOUNT_COLUMN].sum())), "main": main, "transfers_and_cash": transfers_and_cash}


def process_income(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Функция обработки доходов."""
    if dataframe.empty:
        return {"total_amount": 0, "main": []}

    totals = dataframe.groupby(CATEGORY_COLUMN)[AMOUNT_COLUMN].sum().round()
    top_categories = totals.nlargest(3)
    main = [{"category": category, "amount": int(amount)} for category, amount in top_categories.items()]
    return {"total_amount": int(round(dataframe[AMOUNT_COLUMN].sum())), "main": main}


def get_events_data(date_str: str, period: str = "M") -> dict[str, Any]:
    """Функция получения данных по событиям."""
    dataframe = load_excel_data()
    start_date, end_date = calculate_period(date_str, period)
    filtered_data = dataframe[(dataframe[DATE_COLUMN] >= start_date) & (dataframe[DATE_COLUMN] <= end_date)]

    expenses_df = filtered_data[filtered_data[AMOUNT_COLUMN] < 0]
    income_df = filtered_data[filtered_data[AMOUNT_COLUMN] > 0]
    return {
        "expenses": process_expenses(expenses_df),
        "income": process_income(income_df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }
