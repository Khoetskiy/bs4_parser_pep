import csv
import datetime as dt
import logging
from pathlib import Path

from prettytable import RANDOM, PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_arg):
    output = cli_arg.output

    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_arg)
    else:
        # Вывод по умолчанию.
        default_output(results)


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    # Выравниваем всю таблицу по левому краю.
    table.align = 'l'
    # Добавляем все строки, начиная со второй (с индексом 1).
    table.add_rows(results[1:])
    table.set_style(RANDOM)
    print(table)


def file_output(results, cli_arg):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True, parents=True)

    # Получаем режим работы парсера из аргументов командной строки.
    parser_mode = cli_arg.mode

    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)

    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    # if not results_dir.exists() or not results_dir.is_dir():
    #     raise OSError(f'Не удалось создать директорию: {results_dir}')

    # if not results or len(results) == 0:
    #     print('Нет данных для сохранения в файл')
    #     return

    with Path(file_path).open('w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)

    logging.info(f'Файл с результатами был сохранён: {file_path}')
