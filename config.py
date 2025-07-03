"""
Configuration file for database connections.
(Файл конфигурации для подключения к базам данных)
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env
# (Загрузка переменных окружения из файла .env)
load_dotenv()

# MySQL configuration (Настройки для MySQL)
MYSQL_CONFIG = {
    "host":       os.getenv('MYSQL_HOST'),
    "user":       os.getenv('MYSQL_USER'),
    "password":   os.getenv('MYSQL_PASSWORD'),
    "database":   os.getenv('MYSQL_DATABASE'),
    "charset":    "utf8mb4",
    "use_unicode": True
}

# MongoDB configuration (Настройки для MongoDB)
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

