"""
Statistics module for retrieving search logs from MongoDB.
(Модуль статистики для получения логов поиска из MongoDB)
"""

from pymongo import MongoClient
from typing import List, Dict
import config


try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DB_NAME]
    collection = db[config.MONGO_COLLECTION]
except Exception as error:
    print(f"[MongoDB connection error] {error}")
    collection = None


def get_top_searches(limit: int = 5) -> List[Dict]:
    """
    Get top N most frequent search queries (excluding errors).
    (Получает N самых популярных запросов, исключая ошибки)

    Args:
        limit (int): Number of top queries to return.

    Returns:
        List[Dict]: Aggregated query statistics.
    """
    if collection is None:
        return []

    # MongoDB aggregation pipeline: group identical requests and sort by frequency and recency
    pipeline = [
        {"$match": {"search_type": {"$ne": "error"}}},
        {"$group": {
            "_id": {"type": "$search_type", "params": "$params"},
            "count": {"$sum": 1},
            "last_time": {"$max": "$timestamp"}
        }},
        {"$sort": {"count": -1, "last_time": -1}},
        {"$limit": limit}
    ]

    try:
        return [{
            "timestamp": doc["last_time"],
            "search_type": doc["_id"]["type"],
            "params": doc["_id"]["params"]
        } for doc in collection.aggregate(pipeline)]
    except Exception as e:
        print(f"[Aggregation error in get_top_searches()] {e}")
        return []


def get_recent_unique_searches(limit: int = 5) -> List[Dict]:
    """
    Get last N unique search queries by type and parameters.
    (Получает последние уникальные запросы по типу и параметрам)

    Args:
        limit (int): Number of recent unique queries to retrieve.
                     (Сколько уникальных запросов возвращать)

    Returns:
        List[Dict]: Recently logged unique queries.
                    (Список уникальных логов по времени)
    """
    if collection is None:
        return []

    # MongoDB aggregation: take first timestamp per unique query pattern
    pipeline = [
        {"$match": {"search_type": {"$ne": "error"}}},
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": {"type": "$search_type", "params": "$params"},
            "timestamp": {"$first": "$timestamp"}
        }},
        {"$sort": {"timestamp": -1}},
        {"$limit": limit}
    ]

    try:
        return [{
            "timestamp": doc["timestamp"],
            "search_type": doc["_id"]["type"],
            "params": doc["_id"]["params"]
        } for doc in collection.aggregate(pipeline)]
    except Exception as e:
        print(f"[Aggregation error in get_recent_unique_searches()] {e}")
        return []