"""
MongoDB Logger Module
(Модуль логирования событий и действий в MongoDB)

Provides a logger class for recording events into MongoDB and printing
key log entries to the console.
(Предоставляет класс логгера для записи событий в MongoDB и вывода
ключевых записей в консоль.)
"""

from pymongo import MongoClient
from datetime import datetime, timezone
from typing import Callable, Optional
from functools import wraps
import config

class MongoLogger:
    """
    Logger for recording events into MongoDB and printing important logs
    to the console.
    (Логгер для записи событий в MongoDB и вывода важных логов в консоль.)
    """

    def __init__(
        self,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        uri: Optional[str] = None
    ) -> None:
        """
        Initializes the MongoDB client and connects to the specified database
        and collection.
        (Инициализирует клиент MongoDB и подключается к указанной базе и коллекции.)

        Args:
            db_name (Optional[str]): Name of the MongoDB database.
                                     (Имя базы данных MongoDB.)
            collection_name (Optional[str]): Name of the collection to log to.
                                             (Имя коллекции для записи логов.)
            uri (Optional[str]): MongoDB connection URI.
                                 (URI подключения к MongoDB.)
        """
        try:
            self.uri: str = uri or config.MONGO_URI
            self.db_name: str = db_name or config.MONGO_DB_NAME or "movie_search_logs"
            self.collection_name: str = collection_name or config.MONGO_COLLECTION or "logs"

            self.client: MongoClient = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

            # Test MongoDB connection (Проверка соединения с сервером MongoDB)
            self.client.server_info()

            # Log success connection (Лог успешного подключения)
            self.log_event(
                "mongodb_connected",
                {"description": "Logger successfully connected."},
                level="info"
            )
        except Exception as e:
            print(f"[ERROR] MongoDB: connection error → {e}")
            self.collection = None

    def is_connected(self) -> bool:
        """
        Checks if the logger is connected to the MongoDB collection.
        (Проверяет, подключён ли логгер к коллекции MongoDB.)

        Returns:
        bool:
        True if the MongoDB connection is active, otherwise False.
        (True — если соединение с MongoDB установлено, иначе False.)
        """
        return self.collection is not None

    def get_timestamp(self) -> datetime:
        """
        Returns the current UTC timestamp for logs.
        (Возвращает текущую метку времени в формате UTC для логов.)

        Returns:
            datetime:
                Current UTC datetime object.
                (Текущая дата и время в формате UTC.)
        """
        return datetime.now(timezone.utc)

    def log_event(self, event_type: str, data: dict, level: str = "info") -> None:
        """
        Inserts a log entry into MongoDB and prints selected logs to the console.
        (Добавляет лог-запись в MongoDB и выводит сообщения в консоль.)

        Args:
            event_type (str): Event name. (Название события)
            data (dict): Event data. (Данные события)
            level (str): Log level. (Уровень лога)
        """
        if not self.is_connected():
            return

        timestamp = self.get_timestamp()
        entry = {
            "event_type": event_type,
            "data": data,
            "level": level,
            "timestamp": timestamp
        }
        try:
            self.collection.insert_one(entry)
        except Exception as e:
            print(f"[ERROR] MongoLogger: failed to write to MongoDB → {e}")

        # Console output for certain levels (Вывод в консоль для info и error)
        if level in {"info", "error"}:
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            source_map = {
                "startup": "MongoLogger",
                "db_connected": "MySQL",
                "mongodb_connected": "MongoDB",
                "shutdown": "MongoLogger",
                "input_error": "Input"
            }
            source = source_map.get(event_type, event_type)
            description = data.get("description") or str(data)
            print(f"[{level.upper()}] {time_str}  {source}: {description}")

    def log_input_error(self, context: str, user_input: str) -> None:
        """
        Logs an input error with context and invalid input.
        (Логирует ошибку пользовательского ввода.)

        Args:
            context (str): Context of the input. (Контекст ошибки)
            user_input (str): Invalid user input. (Ошибочный ввод)
        """
        print(f"[Input Error] Context: {context} | Input: {user_input}")
        self.log_event(
            "input_error",
            {
                "context": context,
                "invalid_input": user_input
            },
            level="warning"
        )

    def log_action(self, action_name: str, level: str = "debug") -> Callable:
        """
        Decorator for logging function calls and outputs.
        (Декоратор для логирования вызовов функций и их результатов.)

        Args:
            action_name (str):
                Name of the action to be logged.
                (Название действия для логирования.)
            level (str):
                Logging level (e.g., "debug", "info").
                (Уровень логирования, например, "debug", "info".)

        Returns:
            Callable:
                A decorated function that logs its execution.
                (Обёрнутая функция, логирующая своё выполнение.)
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self.log_event(
                    "action_trace",
                    {
                        "action": action_name,
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs),
                        "result": str(result)
                    },
                    level=level
                )
                return result
            return wrapper
        return decorator

    def close(self) -> None:
        """
        Closes MongoDB client connection gracefully.
        (Закрывает соединение с MongoDB.)
        """
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except Exception:
                print("[WARNING] MongoLogger: failed to close MongoDB connection.")