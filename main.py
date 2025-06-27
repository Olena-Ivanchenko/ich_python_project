"""
Main application menu
(Главное меню приложения)
"""
import ui
import mysql_connector
import config
import log_writer
import log_stats
from formatter import format_results


def search_by_keyword_menu(mysql_conn):
    """
    Handle keyword search with pagination and logging.
    (Поиск по ключевому слову + логирование)
    """
    keyword = ui.get_keyword_input()
    offset = 0
    while True:
        results = mysql_connector.search_by_keyword(mysql_conn, keyword, offset=offset)
        ui.show_results(results)
        log_writer.log_search("keyword", {"keyword": keyword}, len(results))
        if len(results) < 10 or not ui.continue_prompt():
            break
        offset += 10


def search_by_genre_and_year_menu(mysql_conn):
    """
    Handle genre and year search with pagination and logging.
    (Поиск по жанру и годам + логирование)
    """
    genres, min_year, max_year = mysql_connector.get_genre_and_years(mysql_conn)
    genre, year_from, year_to = ui.genre_year_input(genres, min_year, max_year)
    if genre:
        offset = 0
        while True:
            results = mysql_connector.search_by_genre_and_year(mysql_conn, genre, year_from, year_to, offset = offset)
            ui.show_results(results)
            log_writer.log_search("genre_year", {
                "genre": genre,
                "year_from": year_from,
                "year_to": year_to
            }, len(results))
            if len(results) < 10 or not ui.continue_prompt():
                break
            offset += 10


def show_statistics_menu():
    """
    Display statistics submenu and handle user selection.
    (Подменю статистики + форматированный вывод)
    """
    choice = ui.show_statistics_menu()
    if choice == "1":
        stats = log_stats.get_top_searches()
        format_results(stats, mode="logs")
    elif choice == "2":
        stats = log_stats.get_recent_unique_searches()
        format_results(stats, mode="logs")
    else:
        ui.show_error("Некорректный выбор статистики.")


def main():
    """
    Main application loop.
    (Основной цикл приложения)
    """
    mysql_conn = mysql_connector.connection(config.MYSQL_CONFIG)
    try:
        ui.print_message("Добро пожаловать в Movie Search! Найдём кино под настроение")
        while True:
            choice = ui.main_menu()
            if choice == 1:
                try:
                    search_by_keyword_menu(mysql_conn)
                except Exception as e:
                    ui.show_error(f"Ошибка при поиске по ключевому слову: {e}")
                    log_writer.log_search("error", {"type": "keyword",
                                                    "message": str(e)}, 0)
            elif choice == 2:
                try:
                    search_by_genre_and_year_menu(mysql_conn)
                except Exception as e:
                    ui.show_error(f"Ошибка при поиске по жанру и годам: {e}")
                    log_writer.log_search("error", {"type": "genre_year",
                                                    "message": str(e)}, 0)
            elif choice == 3:
                show_statistics_menu()
            elif choice == 4:
                ui.print_message("До свидания!")
                break
            else:
                ui.show_error("Пожалуйста, выберите пункт от 1 до 4.")
    finally:
        mysql_conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.print_message("\nПриложение завершено пользователем.")