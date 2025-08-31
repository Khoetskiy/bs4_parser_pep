import logging

from requests import RequestException
from exceptions import ParserFindTagException

logger = logging.getLogger(__name__)


def get_response(session, url):
    """Перехват ошибки RequestException."""
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logger.exception(
            'Возникла ошибка при загрузке страницы %s',
            url,
            stack_info=True,
        )
    # return None


def find_tag(soup, tag, attrs=None):
    """Перехват ошибки поиска тегов."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logger.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
