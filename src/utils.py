from __future__ import annotations

import logging

import requests_cache
from bs4 import BeautifulSoup, Tag
from requests import RequestException

from exceptions import ParserFindTagException, RequestErrorException

logger = logging.getLogger(__name__)


def get_response(
    session: requests_cache.CachedSession, url: str, encoding: str = 'utf-8'
) -> requests_cache.Response:
    """
    Выполняет GET-запрос по указанному URL с использованием переданной сессии.

    Args:
        session: Сессия для выполнения запроса.
        url: URL для запроса.

    Returns:
        requests_cache.Response: Объект ответа, если запрос выполнен успешно.

    Raises:
        RequestErrorException: При ошибке HTTP-запроса.
    """
    try:
        response = session.get(url)
        response.encoding = encoding
    except RequestException as e:
        error_msg = f'Ошибка при загрузке страницы {url}: {e}'
        raise RequestErrorException(error_msg) from e
    else:
        return response


def find_tag(
    soup: BeautifulSoup | Tag, tag: str, attrs: dict | None = None
) -> Tag:
    """
    Находит HTML тег с обязательной проверкой существования.

    Args:
        soup: Объект для поиска.
        tag: Имя HTML тега для поиска.
        attrs: Словарь атрибутов для фильтрации.

    Returns:
        Tag: Найденный HTML элемент.

    Raises:
        ParserFindTagException: Если тег не найден.

    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
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
