import logging
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    CACHED_NAME,
    DOWNLOADS_DIR,
    EXPECTED_STATUS,
    EXPIRE_AFTER_CACHE,
    MAIN_DOC_URL,
    MISMATCH_LOG_TEMPLATE,
    PEP_URL,
)
from exceptions import (
    ParserBaseException,
    ParserFindTagException,
    RequestErrorException,
)
from outputs import control_output
from utils import find_tag, get_response, get_soup

logger = logging.getLogger(__name__)


def whats_new(session: requests_cache.CachedSession) -> list[tuple]:
    """
    Извлекает информацию о новых возможностях из различных версий Python.

    Функция парсит страницу "What's New", получает ссылки на
    документацию для каждой версии, и извлекает заголовки и информацию
    об авторах из каждой версии.

    Args:
        session: Кешированная сессия для HTTP запросов.

    Returns:
        list: Список кортежей (ссылка, заголовок, автор) с заголовками.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    soup = get_soup(session, whats_new_url, 'lxml')
    main = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li', class_='toctree-l1')

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    errors = []

    for section in tqdm(
        sections_by_python,
        colour='blue',
        desc='Парсинг новостей об обновлениях python',
    ):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag.get('href'))

        try:
            soup = get_soup(session, version_link, 'lxml')
        except RequestErrorException as e:
            errors.append(e)
            continue

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
        time.sleep(0.1)

    for error in errors:
        logger.error(error)

    return results


def latest_versions(session: requests_cache.CachedSession) -> list[tuple]:
    """
    Извлекает информацию о доступных версиях Python и их статусах.

    Функция парсит боковую панель главной страницы документации,
    находит список всех версий, и извлекает версию и статус для каждой.

    Args:
        session: Кешированная сессия для HTTP запросов.

    Returns:
        list: Список кортежей (ссылка, версия, статус) с заголовками.

    """
    pattern = r'[Pp]ython (?P<version>\d\.\d+) \((?P<status>.*)\)'

    soup = get_soup(session, MAIN_DOC_URL, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        msg = 'Не найден список версий Python в боковой панели'
        logger.error(msg)
        raise ParserFindTagException(msg)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in tqdm(
        a_tags, colour='blue', desc='Парсинг документаций python'
    ):
        link = a_tag.get('href')
        match = re.search(pattern, a_tag.text)
        if match is not None:
            version, status = match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session: requests_cache.CachedSession) -> None:
    """
    Скачивает архив документации Python в формате PDF.

    Функция находит ссылку на архив PDF на странице загрузок,
    скачивает его и сохраняет в директорию downloads/.

    Args:
        session: Кешированная сессия для HTTP запросов.

    Raises:
        ParserFindTagException: Если не найден необходимый элемент на странице.
        RequestException: При ошибках сетевых запросов.
        OSError: При проблемах с файловой системой.
    """
    logger.info('Начинаем процесс загрузки архива PDF документации')

    download_url = urljoin(MAIN_DOC_URL, 'download.html')
    pattern = r'.+pdf-a4\.zip$'

    soup = get_soup(session, download_url, 'lxml')
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', attrs={'href': re.compile(pattern)})
    href = pdf_a4_tag.get('href')

    if not href:
        error_msg = (
            'Найден тег ссылки на PDF архив, но он не содержит атрибут href. '
            f'Проверьте структуру страницы {download_url}'
        )
        logger.error(error_msg)
        raise ParserFindTagException(error_msg)

    archive_url = urljoin(download_url, href)

    filename = archive_url.split('/')[-1]
    # Тесты требуют создания папки здесь и наличия BASE_DIR
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True, parents=True)
    archive_path = downloads_dir / filename

    if archive_path.exists():
        logger.info(
            'Файл %s уже существует. Архив будет перезаписан.', filename
        )

    response = get_response(session, archive_url)
    with Path(archive_path).open('wb') as f:
        f.write(response.content)

    logger.info('Архив был загружен и сохранён: %s', archive_path)


def pep(session: requests_cache.CachedSession) -> list[tuple]:
    """
    Извлекает информацию о документах PEP для анализа их статусов.

    Выполняет двухэтапный парсинг:
    - Извлекает ссылки на PEP и предварительные статусы из основной таблицы
    - Получает точные статусы со страниц отдельных PEP
    - Сравнивает статусы и логирует несовпадения
    - Подсчитывает количество PEP по статусам

    Args:
        session: Кешированная сессия для HTTP запросов.

    Returns:
        list: Список кортежей (статус, количество) с заголовками и итогом.
    """
    peps_numerical_idx_url = urljoin(PEP_URL, 'numerical')

    results = []
    count_status = {}
    errors = []
    mismatch_statuses = []

    soup = get_soup(session, peps_numerical_idx_url, 'lxml')
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    table_body = find_tag(table_tag, 'tbody')
    rows = table_body.find_all('tr')

    for row in tqdm(
        rows, desc='Парсинг таблицы PEP', colour='blue', unit='строк'
    ):
        try:
            cols = row.find_all('td')
            if not cols:
                continue

            abbr = cols[0].find('abbr')
            preview_status = abbr.text[1:]
            a_tag = find_tag(cols[1], 'a', attrs={'href': True})
            pep_link = urljoin(PEP_URL, a_tag['href'])

            try:
                soup = get_soup(session, pep_link, 'lxml')
            except RequestErrorException as e:
                errors.append(e)
                continue

            section = find_tag(soup, 'section', attrs={'id': 'pep-content'})
            dl = find_tag(section, 'dl', attrs={'class': 'field-list'})
            status = dl.select_one(
                'dt:-soup-contains("Status") + dd'
            ).get_text(strip=True)

            if status not in EXPECTED_STATUS[preview_status]:
                mismatch_statuses.append(
                    MISMATCH_LOG_TEMPLATE.format(
                        pep_link, status, EXPECTED_STATUS[preview_status]
                    )
                )

            count_status[status] = count_status.get(status, 0) + 1
            time.sleep(0.1)
        except ParserBaseException as e:
            errors.append(e)
            continue

    for error in errors:
        logger.error(error)

    for mismatch in mismatch_statuses:
        logger.warning(mismatch)

    results.extend(sorted(count_status.items()))

    return [
        ('Статус', 'Количество'),
        *results,
        ('Total', sum(count for _, count in results)),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logger.info('Парсер запущен!')

        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logger.info('Аргументы командной строки: %s', args)

        session = requests_cache.CachedSession(
            cache_name=CACHED_NAME, expire_after=EXPIRE_AFTER_CACHE
        )

        if args.clear_cache:
            logger.info('Очистка кеша..')
            session.cache.clear()

        parser_mode = args.mode

        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)
    except RequestErrorException:
        logger.exception('Сетевая ошибка при парсинге:')
        return
    except ParserFindTagException:
        logger.exception('Структура страницы изменилась:')
        return
    except ParserBaseException:
        logger.exception('Критическая ошибка парсинга:')
        raise

    logger.info('Парсер завершил работу штатно.')


if __name__ == '__main__':
    main()
