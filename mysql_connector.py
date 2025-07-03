"""
MySQL connector module
(Модуль для работы с MySQL: подключение, поиск, метаданные)

Provides functions for establishing connection to MySQL,
retrieving genres and years metadata,
and searching films by keyword or by genre and year range.
(Предоставляет функции для установления соединения с MySQL,
извлечения метаданных о жанрах и годах выпуска,
а также поиска фильмов по ключевым словам или по жанру и году выпуска.)
"""

from typing import List, Tuple, Dict, Optional, TypedDict
import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector import Error as MySQLError
from log_writer import MongoLogger

# === Constant: pagination size ===
DEFAULT_LIMIT: int = 10  # Количество фильмов на страницу

class FilmRecord(TypedDict):
    """
    Structure of a film record returned from search queries.
    (Структура записи фильма, возвращаемой функциями поиска.)
    """
    title: str                # Название фильма
    release_year: int         # Год выпуска
    rating: Optional[str]     # Рейтинг (может быть None)

def connection(config: dict, logger: Optional[MongoLogger] = None) -> MySQLConnection:
    """
    Establishes a connection to the MySQL database.
    (Устанавливает соединение с базой данных MySQL.)

    Args:
        config (dict): Connection parameters. (Параметры подключения.)
        logger (Optional[MongoLogger]): Logger instance for errors. (Логгер для ошибок.)

    Returns:
        MySQLConnection: Active connection object. (Активное соединение с базой данных)
    """
    try:
        return mysql.connector.connect(**config)
    except MySQLError as err:
        if logger:
            logger.log_event(
                "db_connection_error",
                {"description": "Ошибка подключения к MySQL", "error": str(err)},
                level="error"
            )
        raise
    except Exception as e:
        if logger:
            logger.log_event(
                "db_connection_error",
                {"description": "Неизвестная ошибка подключения к MySQL", "error": str(e)},
                level="error"
            )
        raise

def get_genre_and_years(
    mysql_conn: MySQLConnection,
    logger: Optional[MongoLogger] = None
) -> Tuple[List[str], int, int]:
    """
    Retrieves available genres and release year range.
    (Получает список жанров и диапазон годов выпуска из базы данных.)

    Args:
        mysql_conn (MySQLConnection): Active MySQL connection.
            (Активное подключение к базе данных MySQL.)
    logger (Optional[MongoLogger]): Logger instance for debug/error logging.
        (Экземпляр логгера для отладки и логирования ошибок.)

    Returns:
        Tuple[List[str], int, int]:
            - List of genres (Список жанров),
            - Minimum release year (Минимальный год выпуска),
         - Maximum release year (Максимальный год выпуска)
    """
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute("SELECT name FROM category")
            genres = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT MIN(release_year), MAX(release_year) FROM film")
            min_year, max_year = cursor.fetchone()

        if logger:
            logger.log_event(
                "genre_year_loaded",
                {
                    "genre_count": len(genres),
                    "year_range": f"{min_year}-{max_year}",
                    "description": f"Доступно жанров: {len(genres)}, годы: {min_year}-{max_year}"
                },
                level="debug"
            )
        return genres, min_year, max_year
    except Exception as e:
        if logger:
            logger.log_event(
                "genre_year_error",
                {
                    "description": "Ошибка при получении жанров и годов выпуска",
                    "error": str(e)
                },
                level="error"
            )
        raise

def search_by_keyword(
    mysql_conn: MySQLConnection,
    keyword: str,
    offset: int = 0,
    logger: Optional[MongoLogger] = None
) -> List[FilmRecord]:
    """
    Searches for films by keyword in title or description.
    (Поиск фильмов по ключевому слову в названии или описании.)

    Args:
        mysql_conn (MySQLConnection): MySQL connection. (Соединение с MySQL)
        keyword (str): Search keyword. (Ключевое слово)
        offset (int): Offset for pagination. (Смещение для постраничного вывода)
        logger (Optional[MongoLogger]): Logger. (Логгер)

    Returns:
        List[FilmRecord]: Matching film records.
    """
    if not keyword.strip():
        if logger:
            logger.log_input_error("search_by_keyword", "Пустой поисковый запрос")
        return []

    try:
        with mysql_conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT title, release_year, rating
                FROM film
                WHERE title LIKE %s OR description LIKE %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", DEFAULT_LIMIT, offset))
            results = cursor.fetchall()

        if logger:
            logger.log_event(
                "keyword_search",
                {
                    "keyword": keyword,
                    "returned": len(results),
                    "offset": offset,
                    "description": f"Поиск по ключу '{keyword}' → найдено {len(results)}"
                },
                level="info"
            )
        return results
    except MySQLError as err:
        log_search_error(logger, "keyword", keyword, err)
        return []
    except Exception as e:
        log_search_error(logger, "keyword", keyword, e)
        return []

def search_by_genre_and_year(
    mysql_conn: MySQLConnection,
    genre: str,
    year_from: int,
    year_to: int,
    offset: int = 0,
    logger: Optional[MongoLogger] = None
) -> List[FilmRecord]:
    """
    Searches films by genre and year range.
    (Поиск фильмов по жанру и диапазону годов.)

    Args:
        mysql_conn (MySQLConnection): MySQL connection. (Соединение с БД)
        genre (str): Genre name. (Жанр)
        year_from (int): Start year. (Начальный год)
        year_to (int): End year. (Конечный год)
        offset (int): Offset for pagination. (Смещение постраничного вывода)
        logger (Optional[MongoLogger]): Logger. (Логгер)

    Returns:
        List[FilmRecord]: Matching films.
    """
    try:
        with mysql_conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT f.title, f.release_year, f.rating
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (genre, year_from, year_to, DEFAULT_LIMIT, offset))
            results = cursor.fetchall()

        if logger:
            logger.log_event(
                "genre_search",
                {
                    "genre": genre,
                    "years": f"{year_from}-{year_to}",
                    "returned": len(results),
                    "offset": offset,
                    "description": f"Поиск по жанру '{genre}' за {year_from}-{year_to} → найдено {len(results)}"
                },
                level="info"
            )
        return results
    except MySQLError as err:
        log_search_error(logger, "genre_year", f"{genre}, {year_from}-{year_to}", err)
        return []
    except Exception as e:
        log_search_error(logger, "genre_year", f"{genre}, {year_from}-{year_to}", e)
        return []

def log_search_error(
    logger: Optional[MongoLogger],
    context: str,
    details: str,
    error: Exception
) -> None:
    """
    Centralized error logger for search operations.
    (Централизованное логирование ошибок поиска.)

    Args:
        logger (Optional[MongoLogger]): Logger instance. (Экземпляр логгера)
        context (str): Context string (e.g. 'keyword', 'genre_year'). (Контекст)
        details (str): Details of the failed search. (Детали поиска)
        error (Exception): Exception object. (Исключение)
    """
    if logger:
        logger.log_event(
            "search_error",
            {
                "description": f"Ошибка при поиске ({context}): {details}",
                "error": str(error)
            },
            level="error"
        )