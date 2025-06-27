"""
MySQL connector module
(Модуль для работы с MySQL: подключение, поиск, метаданные)
"""


import mysql.connector
from typing import List, Tuple, Dict


def connection(config: dict) -> mysql.connector.MySQLConnection:
    """
    Establishes a connection to a MySQL database.
    (Устанавливает подключение к базе данных MySQL)

    Args:
        config (dict): A dictionary containing connection parameters.
                       (Словарь с параметрами подключения)

    Returns:
        mysql.connector.MySQLConnection: A live MySQL connection object.
                                         (Объект подключённой базы данных MySQL)
    """
    return mysql.connector.connect(**config)


def get_genre_and_years(mysql_conn) -> Tuple[List[str], int, int]:
    """
    Retrieves the list of all genres and the release year range from the database.
    (Получает список всех жанров и диапазон лет выпуска фильмов из базы данных)

    Args:
        mysql_conn: Active connection to the MySQL database.
                    (Активное соединение с MySQL)

    Returns:
        Tuple[List[str], int, int]: A tuple containing:
    """
    cursor = mysql_conn.cursor()

    cursor.execute("SELECT name FROM category")
    genres = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT MIN(release_year), MAX(release_year) FROM film")
    min_year, max_year = cursor.fetchone()

    cursor.close()
    return genres, min_year, max_year


def search_by_keyword(mysql_conn, keyword: str, offset: int = 0) -> List[Dict]:
    """
    Searches for movies by keyword in the title or description.
    (Ищет фильмы по ключевому слову в названии или описании)

    Args:
        mysql_conn: Active connection to the MySQL database.
        keyword (str): Keyword to search for in the title or description.
        offset (int): Offset for pagination.

    Returns:
        List[Dict]: List of movies matching the search criteria.
                    (Список фильмов, соответствующих условиям поиска)
    """
    cursor = mysql_conn.cursor(dictionary = True)

    query = """
        SELECT title, release_year, rating
        FROM film
        WHERE title LIKE %s OR description LIKE %s
        LIMIT 10 OFFSET %s
    """
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", offset))
    results = cursor.fetchall()

    cursor.close()
    return results


def search_by_genre_and_year(mysql_conn, genre: str, year_from: int, year_to: int, offset: int = 0) -> List[Dict]:
    """
  Searches for movies by genre and release year range.
    (Ищет фильмы по жанру и диапазону лет выпуска)

    Args:
        mysql_conn: Active connection to the MySQL database.
        genre (str): Genre name to filter by.
        year_from (int): Start year of the release range.
        year_to (int): End year of the release range.
        offset (int): Offset value for pagination.

    Returns:
        List[Dict]: List of movies that match the genre and year criteria.
                    (Список фильмов, соответствующих жанру и диапазону лет)
    """
    cursor = mysql_conn.cursor(dictionary=True)

    query = """
        SELECT f.title, f.release_year, f.rating
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
        LIMIT 10 OFFSET %s
    """
    cursor.execute(query, (genre, year_from, year_to, offset))
    results = cursor.fetchall()


    cursor.close()
    return results
