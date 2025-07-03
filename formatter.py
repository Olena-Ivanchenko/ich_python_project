"""
Formatter module for displaying results and logs in tabular format.
(Модуль форматирования: таблицы для логов, статистики, фильмов)

Provides tabular output using the tabulate library for movie and log results.
(Использует библиотеку tabulate для табличного вывода логов и фильмов.)
"""

from typing import List, Dict, Any
from tabulate import tabulate

def format_results(data: List[Dict[str, Any]], mode: str = "logs") -> None:
    """
    Formats and prints results as a table depending on the mode.
    (Форматирует и выводит результаты в виде таблицы в зависимости от режима.)

    Args:
        data (List[Dict[str, Any]]): List of result entries as dictionaries.
                                    (Список записей результатов в виде словарей.)
        mode (str): Display mode: "logs" for logs/statistics,
                    "movies" for film search results.
                    (Режим отображения: "logs" — для логов/статистики,
                    "movies" — для результатов поиска фильмов.)

    Returns:
        None
    """
    if not data:
        print("Нет данных для отображения.")
        return
    if mode == "logs":
        _print_log_table(data)
    elif mode == "movies":
        _print_movie_table(data)
    else:
        print(f"[ОШИБКА] Неизвестный режим отображения: '{mode}'")

def _print_log_table(data: List[Dict[str, Any]]) -> None:
    """
    Prints logs/statistics in tabular format.
    (Выводит логи или статистику запросов в табличной форме.)

    Args:
        data (List[Dict[str, Any]]): List of log/statistic entries.
                                    (Список записей логов или статистики.)

    Returns:
        None
    """
    headers = ["Время", "Тип запроса", "Параметры"]
    rows = []
    for row in data:
        timestamp = row.get("timestamp", "—") or "—"
        event_type = row.get("event_type", "—") or "—"
        params = row.get("params", "") or ""

        # Convert dict params to readable string
        if isinstance(params, dict):
            params = ', '.join(f"{k}: {v}" for k, v in params.items())

        rows.append([timestamp, event_type, params])
    print("\nСтатистика запросов:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def _print_movie_table(data: List[Dict[str, Any]]) -> None:
    """
    Prints movie search results in tabular format.
    (Выводит найденные фильмы в виде таблицы.)

    Args:
        data (List[Dict[str, Any]]): List of movies with keys:
                                    'title', 'release_year', 'rating'.
                                    (Список фильмов с ключами:
                                    'title' — название,
                                    'release_year' — год выпуска,
                                    'rating' — рейтинг.)

    Returns:
        None
    """
    headers = ["Название", "Год", "Рейтинг"]
    rows = []
    for row in data:
        title = row.get("title", "—") or "—"
        year = row.get("release_year", "—") or "—"
        rating = row.get("rating", "—") or "—"
        rows.append([title, year, rating])
    print("\nНайденные фильмы:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))