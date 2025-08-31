import logging
import re
from pathlib import Path
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from utils import find_tag, get_response


def create_cached_session(
    cache_name: str = 'web_cache',
) -> requests_cache.CachedSession:
    """Создает кешированную сессию для всех запросов."""
    return requests_cache.CachedSession(
        cache_name=cache_name, expire_after=3600
    )


def get_page_content(url: str, session: requests_cache.CachedSession) -> str:
    """Загружает HTML контент через кешированную сессию."""
    response = session.get(url)
    response.encoding = 'utf-8'
    response.raise_for_status()  # FIXME: как это работает?
    return response.text


def create_soup(html_content: str, parser: str = 'lxml') -> BeautifulSoup:
    """Создает BeautifulSoup объект из HTML строки."""
    return BeautifulSoup(html_content, features=parser)


def whats_new(session: requests_cache.CachedSession):
    """Что нового."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    # html_content = get_page_content(whats_new_url, session)
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return None
        # continue
    html_content = response.text
    soup = create_soup(html_content, 'lxml')

    # main = soup.find('section', id='what-s-new-in-python')
    main = find_tag(soup, 'section', attrs={'id', 'what-s-new-in-python'})

    # div_with_ul = main.find('div', class_='toctree-wrapper')
    div_with_ul = find_tag(main, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li', class_='toctree-l1')

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for section in tqdm(
        sections_by_python,
        colour='blue',
        desc='Парсинг новостей об обновлениях python',
    ):
        # version_a_tag = section.find('a')
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        # html_content = get_page_content(version_link, session)
        response = get_response(session, version_link)
        if response is None:
            return None
        html_content = response.text

        soup = create_soup(html_content, 'lxml')
        # h1 = soup.find('h1')
        # dl = soup.find('dl')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    pattern = r'[Pp]ython (?P<version>\d\.\d+) \((?P<status>.*)\)'

    # html_content = get_page_content(MAIN_DOC_URL, session)
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None
    html_content = response.text

    soup = create_soup(html_content, 'lxml')

    # sidebar = soup.find('div', class_='sphinxsidebarwrapper')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не найдено')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in tqdm(
        a_tags, colour='blue', desc='Парсинг документаций python'
    ):
        link = a_tag['href']
        match = re.search(pattern, a_tag.text)
        if match is not None:
            version, status = match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    download_url = urljoin(MAIN_DOC_URL, 'download.html')
    pattern = r'.+pdf-a4\.zip$'

    # html_content = get_page_content(download_url, session)
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    html_content = response.text
    soup = create_soup(html_content, 'lxml')

    # main_tag = soup.find('div', {'role': 'main'})
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    # table_tag = main_tag.find('table', class_='docutils')
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    # pdf_a4_tag = table_tag.find('a', {'href': re.compile(pattern)})
    pdf_a4_tag = find_tag(table_tag, 'a', attrs={'href': re.compile(pattern)})
    archive_url = urljoin(download_url, pdf_a4_tag['href'])

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True, parents=True)
    archive_path = downloads_dir / filename

    # Загрузка архива по ссылке
    response = session.get(archive_url)

    # with open(archive_path, 'wb') as f:
    with Path(archive_path).open('wb') as f:
        f.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()  # Запускаем функцию с конфигурацией логов.
    # logger = logging.getLogger(__name__)
    logging.info('Парсер запущен!')

    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()  # Считывание аргументов из командной строки

    logging.info(f'Аргументы командной строки: {args}')

    session = create_cached_session()
    # session = requests_cache.CachedSession()

    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        session.cache.clear()

    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
