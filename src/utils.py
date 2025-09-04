from __future__ import annotations

import logging

import requests_cache

from bs4 import BeautifulSoup
from exceptions import ParserFindTagException, RequestErrorException
from requests import RequestException

logger = logging.getLogger(__name__)


def get_response(
    session: requests_cache.CachedSession, url: str
) -> requests_cache.Response:
    """
    Выполняет GET-запрос по указанному URL с использованием переданной сессии.

    Args:
        session (requests_cache.Session): Сессия для выполнения запроса.
        url (str): URL для запроса.

    Returns:
        requests_cache.Response: Объект ответа, если запрос выполнен успешно.

    Raises:
        RequestErrorException: При ошибке HTTP-запроса.
    """
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except RequestException as e:
        error_msg = f'Ошибка при загрузке страницы {url}: {e}'
        logger.exception(error_msg, stack_info=True)
        raise RequestErrorException(error_msg) from e
    else:
        return response


def find_tag(soup: BeautifulSoup, tag: str, attrs: dict | None = None):
    """
    Находит HTML тег с обязательной проверкой существования.

    Args:
        soup(BeautifulSoup): Объект для поиска.
        tag(str): Имя HTML тега для поиска.
        attrs(dict|None): Словарь атрибутов для фильтрации.

    Returns:
        Tag: Найденный HTML элемент.

    Raises:
        ParserFindTagException: Если тег не найден.

    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logger.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_soup(
    session: requests_cache.CachedSession, url: str, features: str = 'lxml'
) -> BeautifulSoup:
    """
    Создает объект BeautifulSoup из HTML-страницы по указанному URL.

    Args:
        session: Сессия для выполнения HTTP-запроса.
        url: URL-адрес страницы для парсинга.
        features: Парсер, используемый BeautifulSoup (по умолчанию 'lxml').

    Returns:
        BeautifulSoup: Объект для парсинга HTML.

    Raises:
        RequestErrorException: При ошибке HTTP-запроса.
    """
    response = get_response(session, url)
    return BeautifulSoup(response.text, features)


def safe_parse_operation(parse_function, *args, **kwargs):
    """Безопасная обёртка для выполнения операций парсинга."""
    try:
        parse_function(*args, **kwargs)
    except RequestErrorException:
        logger.exception('Сетевая ошибка при парсинге:')
        return
    except ParserFindTagException:
        logger.exception('Структура страницы изменилась:')
        return
    except Exception:
        logger.exception('Критическая ошибка парсинга:')
        raise
