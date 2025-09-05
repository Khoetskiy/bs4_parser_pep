import argparse
import csv
import datetime as dt
import logging
from pathlib import Path

from prettytable import PrettyTable

from constants import (
    DATETIME_FORMAT,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
    RESULTS_DIR,
)

logger = logging.getLogger(__name__)


def default_output(results: list[tuple], *args) -> None:
    """Выводит данные построчно в консоль без форматирования."""
    for row in results:
        print(*row)


def pretty_output(results: list[tuple], *args) -> None:
    """Создаёт отформатированную таблицу для консольного вывода."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: list[tuple], *args) -> None:
    """Сохраняет результаты парсинга в CSV файл."""
    RESULTS_DIR.mkdir(exist_ok=True, parents=True)

    parser_mode = args[0].mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)

    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = RESULTS_DIR / file_name

    with Path(file_path).open('w', encoding='utf-8', newline='') as f:
        csv.writer(f, dialect='unix').writerows(results)

    logger.info('Файл с результатами был сохранён: %s', file_path)


OUTPUT_HANDLERS = {
    OUTPUT_PRETTY: pretty_output,
    OUTPUT_FILE: file_output,
    None: default_output,
}


def control_output(results: list[tuple], cli_arg: argparse.Namespace) -> None:
    """
    Определяет способ вывода результатов парсинга.

    Args:
        results: Данные парсинга.
        cli_arg: Аргументы командной строки.
    """
    output = getattr(cli_arg, 'output', None)
    handler = OUTPUT_HANDLERS.get(output, OUTPUT_HANDLERS[None])
    handler(results, cli_arg)
