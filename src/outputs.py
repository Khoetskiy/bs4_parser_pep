import argparse
import csv
import datetime as dt
import logging

from pathlib import Path
from zoneinfo import ZoneInfo

from constants import BASE_DIR, DATETIME_FORMAT, TIMEZONE
from prettytable import PrettyTable

logger = logging.getLogger(__name__)


def default_output(results: list[tuple]) -> None:
    """Выводит данные построчно в консоль без форматирования."""
    for row in results:
        print(*row)


def pretty_output(results: list[tuple]) -> None:
    """Создаёт отформатированную таблицу для консольного вывода."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: list[tuple], cli_arg: argparse.Namespace) -> None:
    """Сохраняет результаты парсинга в CSV файл."""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True, parents=True)

    parser_mode = cli_arg.mode
    now = dt.datetime.now(tz=ZoneInfo(TIMEZONE))
    now_formatted = now.strftime(DATETIME_FORMAT)

    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    with Path(file_path).open('w', encoding='utf-8', newline='') as f:
        csv.writer(f, dialect='unix').writerows(results)

    logger.info('Файл с результатами был сохранён: %s', file_path)


OUTPUT_HANDLERS = {
    'pretty': lambda results, cli_arg: pretty_output(results),
    'file': file_output,
    None: lambda results, cli_arg: default_output(results),
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
