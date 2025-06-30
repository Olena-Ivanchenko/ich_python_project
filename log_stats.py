"""
Log statistics module for retrieving search data from MongoDB.
(Модуль статистики для получения логов поиска из MongoDB)
"""

from pymongo import MongoClient
import config
import logging

# === Setup logger (Настройка логгера для статистики) ===
logger = logging.getLogger("movie_logger")

# === MongoDB connection (Подключение к MongoDB) ===
try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DB_NAME]
    collection = db[config.MONGO_COLLECTION]
    logger.info("Успешное подключение к MongoDB (log_stats).")
except Exception as e:
    logger.error("Ошибка подключения к MongoDB в log_stats", exc_info=True)
    collection = None


def get_top_searches(limit: int = 5):
    """
    Returns the most frequent search queries.
    (Возвращает наиболее частые поисковые запросы)

    Args:
        limit (int): Number of top queries to return.

    Returns:
        list: List of top search entries.
    """
    if collection is None:
        logger.warning("MongoDB не подключён — get_top_searches()")
        return []

    try:
        pipeline = [
            {"$match": {"search_type": {"$in": ["keyword", "genre_year"]}}},
            {"$group": {
                "_id": {"type": "$search_type", "params": "$params"},
                "count": {"$sum": 1},
                "last": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1, "last": -1}},
            {"$limit": limit}
        ]
        results = collection.aggregate(pipeline)
        return [
            {
                "search_type": doc["_id"]["type"],
                "params": doc["_id"]["params"],
                "timestamp": doc["last"]
            }
            for doc in results
        ]
    except Exception as e:
        logger.error("Ошибка получения популярных запросов", exc_info=True)
        return []


def get_recent_unique_searches(limit: int = 5):
    """
    Returns the most recent unique search queries.
    (Возвращает последние уникальные поисковые запросы)

    Args:
        limit (int): Number of queries to return.

    Returns:
        list: List of unique recent queries.
    """
    if collection is None:
        logger.warning("MongoDB не подключён — get_recent_unique_searches()")
        return []

    try:
        pipeline = [
            {"$match": {"search_type": {"$in": ["keyword", "genre_year"]}}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": {"type": "$search_type", "params": "$params"},
                    "timestamp": {"$first": "$timestamp"}
                }
            },
            {"$sort": {"timestamp": -1}},
            {"$limit": limit}
        ]
        results = collection.aggregate(pipeline)
        return [
            {
                "search_type": doc["_id"]["type"],
                "params": doc["_id"]["params"],
                "timestamp": doc["timestamp"]
            }
            for doc in results
        ]
    except Exception as e:
        logger.error("Ошибка получения последних уникальных запросов", exc_info=True)
        return []