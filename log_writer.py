"""
Log writer module for recording search activity and errors.
(Модуль логирования действий поиска и ошибок в MongoDB и файл)
"""

from pymongo import MongoClient
from datetime import datetime
from typing import Dict
import config
import logging

# === Setup logger (Настройка логгера) ===
logger = logging.getLogger("movie_logger")
logger.setLevel(logging.DEBUG)  # Уровень логирования: DEBUG и выше

if not logger.hasHandlers():
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Лог-файл (только INFO и выше)
    file_handler = logging.FileHandler("errors.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Консольный вывод (всё с DEBUG и выше)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# === MongoDB connection (Подключение к MongoDB) ===
try:
    client: MongoClient = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DB_NAME]
    collection = db[config.MONGO_COLLECTION]
    logger.info("Успешное подключение к MongoDB.")
except Exception as e:
    logger.error("[Ошибка подключения к MongoDB]", exc_info=True)
    collection = None


def log_search(search_type: str, params: Dict, results_count: int) -> None:
    """
    Logs a search query or error into MongoDB with a timestamp.
    (Логирует поисковый запрос или ошибку в MongoDB с отметкой времени)

    Args:
        search_type (str): Type of query — 'keyword', 'genre_year', or 'error'.
                           (Тип запроса — 'keyword', 'genre_year' или 'error')
        params (dict): Parameters of the search or error.
                       (Параметры поиска или ошибки)
        results_count (int): Number of results returned (or 0 in case of error).
                             (Количество возвращённых результатов или 0 при ошибке)
    """
    if collection is None:
        logger.warning("MongoDB не подключен. Запись в лог пропущена.")
        return

    try:
        entry = {
            "search_type": search_type,
            "params": params,
            "results_count": results_count,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(entry)
        logger.info(f"Успешный лог [{search_type}] — {results_count} результатов. Параметры: {params}")
    except Exception as error:
        logger.error("Ошибка при записи в MongoDB", exc_info=True)

