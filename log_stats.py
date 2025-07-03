"""
Log statistics module for Movie Search.
(Модуль статистики логов MongoDB: топ-запросы, уникальные)

Provides functions to retrieve top search queries and recent unique searches
from MongoDB logs with detailed aggregation pipelines and error handling.
(Функции для получения топ-запросов и последних уникальных поисков
из логов MongoDB с использованием агрегатных запросов и обработкой ошибок.)
"""

from typing import List, Dict, Any, Optional
from log_writer import MongoLogger

def get_top_searches(logger: Optional[MongoLogger] = None) -> List[Dict[str, Any]]:
    """
    Returns the top 5 most frequent search queries (by keyword or genre).
    (Возвращает топ-5 самых частых запросов (по ключевому слову и жанру).)

    Args:
        logger (Optional[MongoLogger]): MongoDB logger instance.
            (Экземпляр логгера MongoDB, может быть None.)

    Returns:
        List[Dict[str, Any]]: List of formatted search statistics for display.
            (Список словарей с форматированной статистикой для отображения.)
    """
    if not logger or not logger.is_connected():
        return unavailable_stats("MongoDB")
    try:
        pipeline = [
            {"$match": {"event_type": {"$in": ["search_by_keyword", "search_by_genre_year"]}}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": {
                    "type": "$event_type",
                    "keyword": "$data.keyword",
                    "genre": "$data.genre",
                    "year_from": "$data.year_from",
                    "year_to": "$data.year_to"
                },
                "count": {"$sum": 1},
                "timestamp": {"$first": "$timestamp"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        result = list(logger.collection.aggregate(pipeline))
        formatted: List[Dict[str, Any]] = []
        for r in result:
            etype = r["_id"]["type"]
            timestamp = r["timestamp"]
            count = r["count"]
            if etype == "search_by_keyword":
                keyword = r["_id"].get("keyword", "—")
                event_type = "поиск по слову"
                params = f"'{keyword}' — {count} раз"
            else:
                genre = r["_id"].get("genre", "—")
                y1 = r["_id"].get("year_from", "—")
                y2 = r["_id"].get("year_to", "—")
                event_type = "поиск по жанру"
                params = f"{genre}, {y1}-{y2} — {count} раз"
            formatted.append({
                "timestamp": timestamp,
                "event_type": event_type,
                "params": params
            })
        logger.log_event(
            "stats_top_searches",
            {
                "returned": len(formatted),
                "description": f"Топ-5 самых частых запросов (всего: {len(formatted)})"
            },
            level="debug"
        )
        return formatted
    except Exception as e:
        return log_stats_error(logger, "top_searches", str(e))

def get_recent_unique_searches(logger: Optional[MongoLogger] = None) -> List[Dict[str, Any]]:
    """
    Returns the 5 most recent unique keyword searches.
    (Возвращает 5 последних уникальных поисковых ключевых слов.)

    Args:
        logger (Optional[MongoLogger]): MongoDB logger instance.
            (Экземпляр логгера MongoDB, может быть None.)

    Returns:
        List[Dict[str, Any]]: List of recent unique keyword search stats.
            (Список последних уникальных поисковых запросов.)
    """
    if not logger or not logger.is_connected():
        return unavailable_stats("MongoDB")
    try:
        pipeline = [
            {"$match": {"event_type": "search_by_keyword"}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$data.keyword",
                "timestamp": {"$first": "$timestamp"}
            }},
            {"$sort": {"timestamp": -1}},
            {"$limit": 5}
        ]
        result = list(logger.collection.aggregate(pipeline))
        logger.log_event(
            "stats_recent_unique",
            {
                "returned": len(result),
                "description": f"Последние 5 уникальных запросов — {len(result)} результатов"
            },
            level="debug"
        )
        return [
            {
                "timestamp": r["timestamp"],
                "event_type": "уникальный запрос",
                "params": f"'{r['_id']}'"
            } for r in result
        ]
    except Exception as e:
        return log_stats_error(logger, "recent_unique", str(e))

def unavailable_stats(source: str) -> List[Dict[str, Any]]:
    """
    Returns placeholder if MongoDB or logger is unavailable.
    (Возвращает заглушку, если MongoDB или логгер недоступны.)

    Args:
        source (str):
            Name of the unavailable component (e.g., "MongoDB").
            (Имя недоступного компонента, например, "MongoDB".)

    Returns:
        List[Dict[str, Any]]:
            List with a single stub entry for UI display.
            (Список с одной заглушкой для отображения в интерфейсе.)
    """

    return [{
        "timestamp": "—",
        "event_type": source,
        "params": "недоступна"
    }]

def log_stats_error(logger: Optional[MongoLogger], context: str, error: str) -> List[Dict[str, Any]]:
    """
    Logs error retrieving statistics.
    (Логирует ошибку получения статистики.)

    Args:
        logger (Optional[MongoLogger]):
            Logger instance for recording the error.
            (Экземпляр логгера для записи ошибки.)
        context (str):
            Logical context or function where error occurred.
            (Контекст или функция, где произошла ошибка.)
        error (str):
            Exception message to be logged.
            (Сообщение исключения для логирования.)

    Returns:
        List[Dict[str, Any]]:
            Formatted error entry for UI display.
            (Форматированная запись об ошибке для отображения в интерфейсе.)
    """

    if logger:
        logger.log_event(
            "stats_error",
            {
                "context": context,
                "error": error,
                "description": f"Ошибка при получении статистики: {error}"
            },
            level="error"
        )
    return [{
        "timestamp": "—",
        "event_type": "ошибка",
        "params": f"ошибка при получении статистики ({context})"
    }]