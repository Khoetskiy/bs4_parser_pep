import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    BACKUPCOUNT,
    LOG_DIR,
    LOG_DT_FORMAT,
    LOG_FILE,
    LOG_FORMAT,
    MAXBYTES,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
)


def configure_argument_parser(available_modes):
    """Создаёт и настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера',
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(OUTPUT_PRETTY, OUTPUT_FILE),
        help='Дополнительные способы вывода данных',
    )
    return parser


def configure_logging():
    """Централизовано настраивает логирование для проекта."""
    LOG_DIR.mkdir(exist_ok=True, parents=True)

    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAXBYTES, backupCount=BACKUPCOUNT
    )
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt=LOG_DT_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler()),
        encoding='utf-8',
    )
