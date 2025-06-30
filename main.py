"""
Main application menu
(Главное меню приложения)
"""

import ui
import mysql_connector
import config
from log_writer import log_search, logger
import log_stats
from formatter import format_results


def search_by_keyword_menu(mysql_conn):
    logger.info("Запуск поиска по ключевому слову.")
    keyword = ui.get_keyword_input()
    offset = 0
    try:
        while True:
            results = mysql_connector.search_by_keyword(mysql_conn, keyword, offset=offset)
            ui.show_results(results)
            log_search("keyword", {"keyword": keyword}, len(results))
            logger.debug(f"Найдено {len(results)} результатов по ключевому слову '{keyword}'.")
            if len(results) < 10 or not ui.continue_prompt():
                break
            offset += 10
    except Exception as e:
        logger.error("Ошибка при поиске по ключевому слову", exc_info=True)
        ui.show_error(f"Ошибка: {e}")
        log_search("error", {"type": "keyword", "message": str(e)}, 0)


def search_by_genre_and_year_menu(mysql_conn):
    logger.info("Запуск поиска по жанру и годам.")
    genres, min_year, max_year = mysql_connector.get_genre_and_years(mysql_conn)
    genre, year_from, year_to = ui.genre_year_input(genres, min_year, max_year)
    if genre:
        offset = 0
        try:
            while True:
                results = mysql_connector.search_by_genre_and_year(mysql_conn, genre, year_from, year_to, offset=offset)
                ui.show_results(results)
                log_search("genre_year", {
                    "genre": genre,
                    "year_from": year_from,
                    "year_to": year_to
                }, len(results))
                logger.debug(f"Найдено {len(results)} фильмов в жанре '{genre}' за {year_from}-{year_to}.")
                if len(results) < 10 or not ui.continue_prompt():
                    break
                offset += 10
        except Exception as e:
            logger.error("Ошибка при поиске по жанру и годам", exc_info=True)
            ui.show_error(f"Ошибка: {e}")
            log_search("error", {"type": "genre_year", "message": str(e)}, 0)


def show_statistics_menu():
    logger.info("Показ меню статистики.")
    choice = ui.show_statistics_menu()
    if choice == "1":
        logger.info("Показ популярных запросов.")
        try:
            stats = log_stats.get_top_searches()
            logger.debug(f"Получено {len(stats)} популярных запросов.")
            format_results(stats, mode="logs")
        except Exception as e:
            logger.error("Ошибка при получении популярных запросов", exc_info=True)
            ui.show_error(f"Ошибка статистики: {e}")
    elif choice == "2":
        logger.info("Показ последних уникальных запросов.")
        try:
            stats = log_stats.get_recent_unique_searches()
            logger.debug(f"Получено {len(stats)} уникальных запросов.")
            format_results(stats, mode="logs")
        except Exception as e:
            logger.error("Ошибка при получении последних уникальных запросов", exc_info=True)
            ui.show_error(f"Ошибка статистики: {e}")
    else:
        ui.show_error("Некорректный выбор статистики.")
        logger.warning("Пользователь выбрал недопустимый пункт статистики.")


def main():
    """
    Main application loop.
    (Основной цикл приложения)
    """
    mysql_conn = mysql_connector.connection(config.MYSQL_CONFIG)
    logger.info("Успешное подключение к MySQL.")
    logger.info("Приложение запущено.")

    print()  # 🔹 Чистая строка для отделения логов от интерфейса

    try:
        ui.print_message("Добро пожаловать в Movie Search! Найдём кино под настроение")
        while True:
            choice = ui.main_menu()
            logger.debug(f"Выбор пользователя в главном меню: {choice}")

            if choice == 1:
                search_by_keyword_menu(mysql_conn)
            elif choice == 2:
                search_by_genre_and_year_menu(mysql_conn)
            elif choice == 3:
                show_statistics_menu()
            elif choice == 4:
                ui.print_message("До свидания!")
                logger.info("Выход из приложения пользователем.")
                break
            else:
                ui.show_error("Пожалуйста, выберите пункт от 1 до 4.")
                logger.warning(f"Недопустимый выбор в меню: {choice}")
    finally:
        mysql_conn.close()
        logger.info("Соединение с MySQL закрыто.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.print_message("\nПриложение завершено пользователем.")
        logger.info("Завершение через KeyboardInterrupt.")
