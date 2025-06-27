"""
Formatter module for displaying results.
(Модуль форматирования результатов)
"""

from typing import List, Dict
from tabulate import tabulate


def format_results(data: List[Dict], mode: str = "movies") -> None:
    """
    Formats and displays data as a table using tabulate.
    (Форматирует и выводит данные в виде таблицы с помощью tabulate)

    Args:
        data (List[Dict]): List of dictionaries representing search results.
        mode (str): Display mode — 'movies' for films or 'logs' for search history.

    Returns:
        None
    """
    if not data:
        print("Нет данных для отображения.")
        return

    # Handle movie result formatting (Обработка вывода фильмов)
    if mode == "movies":
        headers = ["Название", "Год", "Рейтинг"]
        table = [
            [
                row.get("title", "—"),
                row.get("release_year", "—"),
                row.get("rating", "—")
            ]
            for row in data
        ]

    # Handle search log formatting (Обработка вывода логов поиска)
    elif mode == "logs":
        headers = ["Время", "Тип запроса", "Параметры"]
        table = [
            [
                str(row.get("timestamp", "—"))[:19],  # Обрезаем микросекунды
                row.get("search_type", "—"),
                ', '.join(f"{k}: {v}" for k, v in row.get("params", {}).items())  # Читаемые параметры
            ]
            for row in data
        ]

    else:
        print("Неизвестный режим отображения.")
        return

    # Output formatted table (Вывод отформатированной таблицы)
    print("\n" + tabulate(table, headers = headers, tablefmt = "grid", stralign = "left"))