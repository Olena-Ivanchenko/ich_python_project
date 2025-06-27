"""
Log writer module for recording search activity in MongoDB.
(Модуль логирования действий поиска в MongoDB)
"""


from pymongo import MongoClient
from datetime import datetime
from typing import Dict
import config


# MongoDB connection (Логгер MongoDB)
try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DB_NAME]
    collection = db[config.MONGO_COLLECTION]
except Exception as e:
    print(f"[Ошибка подключения к MongoDB] {e}")
    collection = None


def log_search(search_type: str, params: Dict, results_count: int) -> None:
    """
  Logs a search query or error into MongoDB with a timestamp.
    (Логирует поисковый запрос или ошибку в MongoDB с отметкой времени)

    Args:
        search_type (str): Type of query — 'keyword', 'genre_year', or 'error'.
        params (dict): Parameters of the search or error.
        results_count (int): Number of results returned (or 0 in case of error).

    Returns:
        None
    """
    if collection is None:
        print("[Предупреждение] MongoDB не подключен, лог не записан.")
        return

    try:
        entry = {
            "search_type": search_type,
            "params": params,
            "results_count": results_count,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(entry)
    except Exception as error:
        print(f"[Ошибка записи в MongoDB] {error}")
