"""
Main application module for the Movie Search project.
(Главный модуль приложения "Movie Search")

Handles application startup, main loop, user input routing,
database connections, logging, and graceful shutdown.
(Обрабатывает запуск приложения, главный цикл, маршрутизацию пользовательского ввода,
подключения к базе данных, логирование и корректное завершение работы.)
"""

import config
import mysql_connector
import user_interface as ui
import formatter
from log_writer import MongoLogger
from log_stats import get_top_searches, get_recent_unique_searches
from typing import Callable, Any

def log_keyword_summary(keyword: str, found_count: int, logger: MongoLogger) -> None:
    """
    Logs the summary of a keyword search event.
    (Логирует результат поиска по ключевому слову.)

    Args:
        keyword (str): Search keyword. (Ключевое слово для поиска)
        found_count (int): Number of results found. (Количество найденных результатов)
        logger (MongoLogger): Logger instance. (Экземпляр логгера)
    """
    status = "found" if found_count > 0 else "not_found"
    logger.log_event(
        "keyword_summary",
        {
            "keyword": keyword,
            "status": status,
            "found_count": found_count
        },
        level="info"
    )

def show_paginated_results(
    search_func: Callable[..., list],
    *args: Any,
    logger: MongoLogger
) -> None:
    """
    Displays paginated search results, handles continuation and input retries.
    (Отображает результаты поиска постранично, обрабатывает запросы на продолжение.)

    Args:
        search_func (Callable[..., list]): Search function. (Функция поиска)
        *args (Any): Arguments to pass to search function. (Аргументы для функции поиска)
        logger (MongoLogger): Logger instance. (Экземпляр логгера)
    """
    offset = 0
    while True:
        results = search_func(*args, offset=offset, logger=logger)

        # Log only the first page for keyword search (Лог только при первой странице для ключевого слова)
        if offset == 0 and search_func.__name__ == "search_by_keyword":
            keyword = args[1] if len(args) > 1 else ""
            log_keyword_summary(keyword, len(results), logger)

        ui.show_results(results)

        if not results:
            ui.print_message("По вашему запросу ничего не найдено.")
            if not ui.continue_or_menu_prompt(logger):
                break
            new_keyword = ui.get_keyword_input(logger)
            offset = 0
            args = (args[0], new_keyword)
            continue

        if len(results) < 10 or not ui.continue_prompt(logger):
            break
        offset += 10

def main() -> None:
    """
    Entry point of the Movie Search application.
    (Точка входа в приложение Movie Search.)

    Sets up logging, database connections, runs main menu loop,
    and ensures graceful shutdown.
    (Настраивает логирование, подключение к базе данных,
    запускает главный цикл меню и обеспечивает корректное завершение работы.)
    """
    logger = MongoLogger()
    logger.log_event("startup", {"description": "MongoLogger успешно инициализирован."}, level="info")

    try:
        mysql_conn = mysql_connector.connection(config.MYSQL_CONFIG, logger=logger)
        logger.log_event(
            "db_connected",
            {"description": f"Установлено соединение с MySQL на хосте {config.MYSQL_CONFIG['host']}"},
            level="info"
        )
    except Exception as e:
        ui.show_error("Ошибка подключения к базе данных. Попробуйте позже.", logger=logger)
        logger.log_event(
            "db_connection_error",
            {"description": "Ошибка подключения к MySQL", "error": str(e)},
            level="error"
        )
        return

    ui.print_separator()
    ui.print_message("Добро пожаловать в Movie Search! Найдём кино под настроение")
    ui.print_separator()

    while True:
        choice = ui.main_menu(logger)

        if choice == 1:
            # Keyword search (Поиск по ключевому слову)
            keyword = ui.get_keyword_input(logger)
            logger.log_event("search_by_keyword", {"keyword": keyword}, level="info")
            show_paginated_results(mysql_connector.search_by_keyword, mysql_conn, keyword, logger=logger)

        elif choice == 2:
            # Genre + year range search (Поиск по жанру и годам)
            genres, min_year, max_year = mysql_connector.get_genre_and_years(mysql_conn, logger=logger)
            genre, year_from, year_to = ui.genre_year_input(genres, min_year, max_year, logger=logger)
            if genre is None:
                continue
            logger.log_event(
                "search_by_genre_year",
                {"genre": genre, "year_from": year_from, "year_to": year_to},
                level="info"
            )
            show_paginated_results(
                mysql_connector.search_by_genre_and_year,
                mysql_conn,
                genre,
                year_from,
                year_to,
                logger=logger
            )

        elif choice == 3:
            # View statistics (Просмотр статистики)
            ui.print_statistics_menu()
            stat_choice = ui.get_statistics_choice(logger)
            results = (
                get_top_searches(logger=logger)
                if stat_choice == "1"
                else get_recent_unique_searches(logger=logger)
            )
            formatter.format_results(results, mode="logs")

        elif choice == 4:
            # Exit (Выход из программы)
            ui.print_message("Спасибо за использование Movie Search. До встречи!")
            logger.log_event(
                "shutdown",
                {"description": "Пользователь завершил работу с приложением"},
                level="info"
            )
            break

    logger.close()

if __name__ == "__main__":
    main()