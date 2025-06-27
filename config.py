"""
Configuration file for database connections.
(Файл конфигурации для подключения к базам данных)
"""

MYSQL_CONFIG = {
    "host":       "ich-db.edu.itcareerhub.de",
    "user":       "ich1",
    "password":   "password",
    "database":   "sakila",
    "charset":    "utf8mb4",
    "use_unicode": True
}


# Параметры MongoDB
MONGO_URI = "mongodb://ich_editor:verystrongpassword" "@mongo.itcareerhub.de/?readPreference=primary" "&ssl=false&authMechanism=DEFAULT&authSource=ich_edit"
MONGO_DB_NAME = "ich_edit"
MONGO_COLLECTION = "final_project_100125dam_Olena_Ivanchenko"
