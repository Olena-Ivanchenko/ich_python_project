"""
UI module for interacting with the user and launching the program.
(Модуль пользовательского интерфейса для взаимодействия с пользователем и запуска программы)
"""
from typing import List, Tuple, Optional
from tabulate import tabulate
from typing import List, Dict

def main_menu() -> int:
    """
    Display the main menu and return user's choice.
    (Показывает главное меню и возвращает выбор пользователя)

    Returns:
        int: User selection (1–4), or 0 on invalid input.
    """
    prompt = """
    === МЕНЮ ===
    1. Поиск по ключевому слову
    2. Поиск по жанру и годам
    3. Статистика поисков
    4. Выход
    Выберите пункт (1-4): """
    try:
        return int(input(prompt))
    except ValueError:
        print("Ошибка: введите число от 1 до 4.")
        return 0


def get_keyword_input() -> str:
    """
    Prompt user to enter a keyword for title search.
    (Запрашивает у пользователя ключевое слово для поиска по названию)

    Returns:
        str: Entered keyword.(Введенное ключевое слово)
    """
    return input("Введите ключевое слово или часть названия фильма: ")


def genre_year_input(genre_list: List[str], min_year: int, max_year: int) -> Tuple[Optional[str], int, int]:
    """
    Ask user to select a genre and year range.
    (Запрашивает у пользователя жанр и диапазон лет)

    Args:
        genre_list (List[str]): Available genres.
        min_year (int): Minimum year in the database.
        max_year (int): Maximum year in the database.

    Returns:
        Tuple[Optional[str], int, int]: Selected genre, start year, end year. Returns (None, 0, 0) on input error.
    """
    print(" \n Доступные жанры:")
    for genre in genre_list:
        print("-", genre)
    print(f"Доступный диапазон лет: {min_year} - {max_year}")

    genre = input("Введите выбранный жанр: ")
    try:
        year_from = int(input("С какого года: "))
        year_to = int(input("По какой год: "))
    except ValueError:
        print("Ошибка: годы должны быть числами.")
        return None, 0, 0

    return genre, year_from, year_to

def show_statistics_menu() -> str:
    """
    Display options for statistics view.
    (Показывает меню выбора статистики)

    Returns:
        str:'1' or '2' depending on user's selection.
    """
    print("\nСТАТИСТИКА:")
    print("1. Популярные запросы")
    print("2. Последние уникальные запросы")
    return input("Выберите вариант (1 или 2): ")

def continue_prompt() -> bool:
    """
    Ask user if they want to continue pagination.
    (Спрашивает, хочет ли пользователь продолжить просмотр)

    Returns:
        bool: True if user inputs 'y' or 'Y', False otherwise.
    """
    return input("Показать ещё? (y/n): ").strip().lower() == "y"

def print_message(message: str) -> None:
    """
    Print general-purpose message.
    (Печатает общее сообщение пользователю)

    Args:
        message (str): Message to print.
    """
    print(f"\n{message}")

def show_error(message: str) -> None:
    """
    Display an error message to user.
    (Показывает сообщение об ошибке)

    Args:
        message (str): Error message to print.
    """
    print(f"\n[ОШИБКА] {message}")


def show_results(results: List[Dict]) -> None:
    """
    Displays a list of movies as a table using tabulate
    (Показывает список фильмов в виде таблицы с использованием tabulate.)

    Args:
        results (List[Dict]): List of movies.
    """
    if not results:
        print("Ничего не найдено.")
        return

    table = [[row.get("title", "—"), row.get("release_year", "—"), row.get("rating", "—")] for row in results]
    headers = ["Название", "Год", "Рейтинг"]

    print("\n" + tabulate(table, headers=headers, tablefmt="grid", stralign="left"))


def show_statistics(title: str, queries: List[dict]) -> None:
    """
    Show a statistics block (top or recent queries).
    (Отображает блок статистики: топ или последние запросы)

    Args:
        title (str): Section title to display.
        queries (List[dict]): List of statistics entries from MongoDB.
    """
    print(f"\n--- {title} ---")
    if not queries:
        print("Нет данных.")
        return

    for entry in queries:
        timestamp = entry.get("timestamp", "—")
        search_type = entry.get("search_type", "—")
        params = entry.get("params", {})
        print(f"{timestamp} | {search_type} | {params}")