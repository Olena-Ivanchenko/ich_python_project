"""
User Interface module
(Модуль пользовательского интерфейса (UI))
"""

from typing import List, Tuple, Optional, Dict, Set
from formatter import format_results
from log_writer import MongoLogger
import sys

def main_menu(logger: MongoLogger) -> int:
    """
    Displays the main menu and returns the selected option.
    (Отображает главное меню и возвращает выбранный пункт.)

    Args:
        logger (MongoLogger): Logging instance for error tracking.
                              (Экземпляр логгера для отслеживания ошибок)

    Returns:
        int: Chosen menu option.
             (Выбранный пункт меню)
    """
    print_message("=== МЕНЮ ===")
    print("1. Поиск по ключевому слову")
    print("2. Поиск по жанру и годам")
    print("3. Статистика поисков")
    print("4. Выход")
    return int_input_prompt("Выберите пункт (1-4): ", {1, 2, 3, 4}, logger, "main_menu")

def get_keyword_input(logger: MongoLogger) -> str:
    """
    Requests and validates the keyword for search.
    (Запрашивает ключевое слово и проверяет его.)

    Returns:
        str: Valid keyword string.
             (Корректное ключевое слово)
    """
    while True:
        try:
            keyword: str = input("Введите ключевое слово или часть названия фильма: ").strip()
            if keyword:
                return keyword
            show_error("Ошибка: ключевое слово не может быть пустым.")
            logger.log_input_error("get_keyword_input", keyword)
        except KeyboardInterrupt:
            graceful_exit(logger)

def genre_year_input(
    genre_list: List[str],
    min_year: int,
    max_year: int,
    logger: MongoLogger
) -> Tuple[Optional[str], int, int]:
    """
    Prompts the user to choose a genre and enter a valid year range.
    (Запрашивает выбор жанра и диапазон годов.)

    Returns:
        Tuple[Optional[str], int, int]: Selected genre, year_from, year_to
                                        (Выбранный жанр, начало и конец диапазона)
    """
    print_genre_list(genre_list)
    print_year_range(min_year, max_year)
    while True:
        try:
            genre_input: str = input("Введите выбранный жанр (или 'q' для выхода): ").strip().lower()
            if genre_input == "q":
                return None, 0, 0
            matched_genre = next((g for g in genre_list if g.lower() == genre_input), None)
            if matched_genre:
                break
            show_error("Ошибка: выбранный жанр отсутствует в списке. Попробуйте снова.")
            logger.log_input_error("genre_input", genre_input)
        except KeyboardInterrupt:
            graceful_exit(logger)

    while True:
        try:
            year_from = int(input("С какого года: "))
            year_to = int(input("По какой год: "))
            if year_from > year_to:
                raise ValueError("Начало диапазона позже конца")
            if year_from < min_year or year_to > max_year:
                raise ValueError("Год вне допустимого диапазона")
            break
        except ValueError as e:
            show_error("Ошибка: введите корректные числа и проверьте диапазон.")
            logger.log_input_error("year_range_input", str(e))
        except KeyboardInterrupt:
            graceful_exit(logger)

    return matched_genre, year_from, year_to

def continue_prompt(logger: MongoLogger) -> bool:
    """
    Asks if the user wants to continue viewing results.
    (Запрашивает, хочет ли пользователь продолжить просмотр результатов.)

    Returns:
        bool: True if user agrees to continue.
              (True, если пользователь хочет продолжить)
    """
    return yes_no_prompt("Показать ещё? (y/n): ", logger, "continue_prompt")

def continue_or_menu_prompt(logger: MongoLogger) -> bool:
    """
    Asks whether to continue search or return to the main menu.
    (Запрашивает, продолжить поиск или вернуться в меню.)

    Returns:
        bool: True to continue search, False to go to menu.
              (True — продолжить, False — в меню)
    """
    return yes_no_prompt("Продолжить поиск? (y - да, n - в главное меню): ", logger, "continue_or_menu_prompt")

def get_statistics_choice(logger: MongoLogger) -> str:
    """
    Gets the user's choice for statistics view.
    (Получает выбор статистики: популярные или уникальные запросы.)

    Returns:
        str: Selected option ('1' or '2')
             (Выбранный вариант: '1' или '2')
    """
    print_statistics_menu()
    return str_input_prompt("Выберите вариант (1 или 2): ", {"1", "2"}, logger, "statistics_menu")

def yes_no_prompt(prompt: str, logger: MongoLogger, context: str) -> bool:
    """
    Generic yes/no input handler.
    (Обработка ввода 'да'/'нет'.)

    Returns:
        bool: True for yes, False for no.
              (True — да, False — нет)
    """
    while True:
        try:
            choice = input(prompt).strip().lower()
            if choice in {"y", "yes"}:
                return True
            if choice in {"n", "no"}:
                return False
            show_error("Пожалуйста, введите 'y' или 'n'.")
            logger.log_input_error(context, choice)
        except KeyboardInterrupt:
            graceful_exit(logger)

def int_input_prompt(prompt: str, valid: Set[int], logger: MongoLogger, context: str) -> int:
    """
    Validates user integer input against a set of valid options.
    (Проверяет целочисленный ввод пользователя.)

    Returns:
        int: Validated user choice.
             (Подтверждённый выбор пользователя)
    """
    while True:
        try:
            value = input(prompt).strip()
            number = int(value)
            if number in valid:
                return number
            raise ValueError
        except ValueError:
            show_error(f"Ошибка: введите число из допустимого диапазона: {sorted(valid)}")
            logger.log_input_error(context, value)
        except KeyboardInterrupt:
            graceful_exit(logger)

def str_input_prompt(prompt: str, valid: Set[str], logger: MongoLogger, context: str) -> str:
    """
    Validates string input against a set of valid options.
    (Проверяет строковый ввод пользователя.)

    Returns:
        str: Validated user input.
             (Корректный ввод)
    """
    while True:
        try:
            choice = input(prompt).strip()
            if choice in valid:
                return choice
            show_error(f"Ошибка: допустимые значения — {', '.join(valid)}.")
            logger.log_input_error(context, choice)
        except KeyboardInterrupt:
            graceful_exit(logger)

def show_results(results: List[Dict]) -> None:
    """
    Displays search results in table format.
    (Показывает найденные фильмы в виде таблицы.)
    """
    format_results(results, mode="movies")

def show_error(message: str) -> None:
    """
    Displays an error message.
    (Выводит сообщение об ошибке.)
    """
    print(f"\n[ОШИБКА] {message}")

def print_message(message: str) -> None:
    """
    Prints a general message with spacing.
    (Печатает сообщение с отступом.)
    """
    print(f"\n{message}")

def print_separator() -> None:
    """
    Prints a visual separator line.
    (Печатает разделительную линию.)
    """
    print("\n" + "-" * 40)

def print_genre_list(genre_list: List[str]) -> None:
    """
    Displays available genres.
    (Показывает список жанров.)
    """
    print_message("Доступные жанры:")
    for genre in genre_list:
        print(f"- {genre}")

def print_year_range(min_year: int, max_year: int) -> None:
    """
    Displays the available range of years.
    (Показывает доступный диапазон годов.)
    """
    print_message(f"Доступный диапазон лет: {min_year} - {max_year}")

def print_statistics_menu() -> None:
    """
    Displays the statistics menu options.
    (Отображает меню статистики.)
    """
    print_message("СТАТИСТИКА:")
    print("1. Популярные запросы")
    print("2. Последние уникальные запросы")

def graceful_exit(logger: MongoLogger) -> None:
    """
    Handles graceful exit on KeyboardInterrupt (Ctrl+C).
    (Корректный выход при прерывании программы через Ctrl+C.)
    """
    print("\n\n[INFO] Работа приложения прервана пользователем. До свидания!")
    logger.log_event("shutdown", {"description": "Приложение завершено пользователем через Ctrl+C"}, level="info")
    sys.exit(0)