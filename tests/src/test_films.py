from http import HTTPStatus
from math import ceil

import pytest

from ..testdata.models_data import Film, FilmShort


@pytest.mark.asyncio
async def test_film_id(films_data, films_fill_data, make_get_request, redis_clean):
    film_id = films_data[0].id
    response = await make_get_request(f'/films/{film_id}')

    assert response.status == HTTPStatus.OK

    return_film = Film(**response.body)
    check_film = films_data[0]
    check_film.actors_names = None
    check_film.writers_names = None
    assert check_film == return_film

    response = await make_get_request('/films/00000000-0000-0000-0000-000000000')
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_film_list_pagination(films_data, films_fill_data, make_get_request, redis_clean):
    page_size = 3
    last_page_number = ceil(len(films_data) / page_size)
    last_page_size = len(films_data) % page_size

    # First page
    response = await make_get_request('/films', params={'size': page_size})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] is None
    assert response.body['next'] == 2
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == page_size

    # Second page
    response = await make_get_request('/films', params={'size': page_size, 'page': 2})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] == 1
    assert response.body['next'] == 3
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == page_size

    # Last page
    response = await make_get_request('/films', params={'size': page_size, 'page': last_page_number})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] == last_page_number - 1
    assert response.body['next'] is None
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == last_page_size


@pytest.mark.asyncio
async def test_film_list_pagination_incorrect_pages(films_data, films_fill_data,
                                                    make_get_request, redis_clean):
    page_size = 3
    last_page_number = ceil(len(films_data) / page_size)

    # The page number less than 1
    response = await make_get_request('/films', params={'size': page_size, 'page': -1})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    # The page number more than last page number
    response = await make_get_request('/films', params={'size': page_size, 'page': last_page_number + 1})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 0


@pytest.mark.asyncio
async def test_film_filtered(films_data, films_fill_data, make_get_request, redis_clean,
                             genres_data, genres_fill_data):
    genre_id = genres_data[1].id
    short_films_data = [FilmShort(**data.dict()) for data in films_data]

    response = await make_get_request('/films', params={'filter': genre_id})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 2

    assert response.body['data'][0] == short_films_data[7].dict()
    assert response.body['data'][1] == short_films_data[3].dict()


@pytest.mark.asyncio
async def test_film_list_sort(films_data, films_fill_data, make_get_request, redis_clean):
    sorted_films_data = sorted(films_data, key=lambda f: f.imdb_rating)
    short_films_data = [FilmShort(**data.dict()) for data in sorted_films_data]

    response = await make_get_request('/films', params={'sort': 'imdb_rating:asc'})
    assert response.status == HTTPStatus.OK
    assert response.body['data'][0] == short_films_data[0].dict()
    assert response.body['data'][1] == short_films_data[1].dict()

    response = await make_get_request('/films', params={'sort': 'imdb_rating:desc'})
    assert response.body['data'][0] == short_films_data[-1].dict()
    assert response.body['data'][1] == short_films_data[-2].dict()


@pytest.mark.asyncio
async def test_film_search(films_data, films_fill_data, make_get_request, redis_clean):

    response = await make_get_request('/films/search/', params={'query': 'Star'})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 2

    response = await make_get_request('/films/search/', params={'query': 'The'})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 0

    response = await make_get_request('/films/search/', params={'query': 'NotTitle'})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 0

    response = await make_get_request('/films/search/', params={'query': 'Звезда'})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 1
