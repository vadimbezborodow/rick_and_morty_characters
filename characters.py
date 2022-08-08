import requests

count_characters = requests.get('https://rickandmortyapi.com/api/character/').json()['info']['count']


def check_page(page: str, url: str) -> int | None:
    """Проверка переданной страницы на существование"""
    try:
        count_pages = requests.get(url).json()['info']['pages']
    except KeyError:
        return None

    if page is None:
        return 1
    elif page.isdigit() and 1 <= int(page) <= count_pages:
        return int(page)

    return None


def modify_form(form: dict[str, str]) -> str:
    """Преобразование запроса от пользователя в url"""
    url_request = ''
    for key in form:
        if form[key] is not None and form[key] != 'Status' and form[key] != 'Gender':
            url_request += f'{key}={form[key]}&'

    # убираем последний символ &
    return url_request[:-1]


def check_request(url_request: str) -> str | None:
    """Проверка на существование запроса, который пришел от пользователя"""
    check_url = f'https://rickandmortyapi.com/api/character/?{url_request}'
    if 'error' in requests.get(check_url).json():
        return

    return 'OK'


def get_all_characters(page: str) -> tuple[dict[str, int], dict] | None:
    """Получение списка персонажей мультсериала по переданной странице"""
    url = 'https://rickandmortyapi.com/api/character/'

    # валидация страницы
    page = check_page(page=page, url=url)
    if page is None:
        return

    # делаем запрос по нужной странице
    url += f'?page={page}'
    characters = requests.get(url).json()

    # получаем url следующей и предыдущей страницы
    next_page, prev_page = characters['info']['next'], characters['info']['prev']

    # если предыдущая и/или следующая страница есть, преобразуем их в целочисленный вид
    if next_page is not None:
        next_page = page + 1

    if prev_page is not None:
        prev_page = page - 1

    pages = {'current_page': page, 'next_page': next_page, 'prev_page': prev_page}

    return pages, characters['results']


def get_filter_characters(page: str, name: str, status: str, gender: str) -> tuple[dict, dict] | None:
    """Получение отфильтрованного списка персонажей мультсериала по форме"""
    url = 'https://rickandmortyapi.com/api/character/?'

    # модифицирование запроса из формы в нужный вид для url
    form = {'name': name, 'status': status, 'gender': gender}
    url_request = modify_form(form=form)

    # проверка существующего запроса по форме
    if check_request(url_request) is None:
        return {}, {}

    # валидация страницы
    page = check_page(page=page, url=url + url_request)
    if page is None:
        return

    url += f'page={page}&' + url_request

    filter_characters = requests.get(url).json()

    # получаем url следующей и предыдущей страницы
    next_page, prev_page = filter_characters['info']['next'], filter_characters['info']['prev']

    # если предыдущая и/или следующая страница есть, преобразуем их в целочисленный вид
    if next_page is not None:
        next_page = f'?page={page + 1}&' + url_request

    if prev_page is not None:
        prev_page = f'?page={page - 1}&' + url_request
    page_url = f'?page={page}&' + url_request

    pages = {'current_page': {'page': page, 'page_url': page_url}, 'next_page': next_page, 'prev_page': prev_page}

    return pages, filter_characters['results']


def get_single_character(id_: str) -> tuple[dict[str, str], dict[str, str]]:
    """Получение информации об одном единственном персонаже"""
    url = f'https://rickandmortyapi.com/api/character/{id_}'
    character = requests.get(url).json()

    # делаем запрос по эпизодам, чтобы получить их название
    first_seen_episode = requests.get(character['episode'][0]).json()['name']
    last_seen_episode = requests.get(character['episode'][-1]).json()['name']

    info = {
        'name': character['name'],
        'status': character['status'],
        'species': character['species'],
        'gender': character['gender'],
        'origin': character['origin']['name'],
        'location': character['location']['name'],
        'image': character['image'],
        'first_seen': first_seen_episode,
        'last_seen': last_seen_episode,
    }

    prev_character = str(int(id_) - 1) if int(id_) - 1 != 0 else ''
    next_character = str(int(id_) + 1) if int(id_) + 1 <= count_characters else ''

    other = {'count': count_characters, 'prev_character': prev_character, 'next_character': next_character}

    return other, info
