from http import HTTPStatus
from math import ceil

import pytest


@pytest.mark.asyncio
async def test_genre(genres_data, genres_fill_data, make_get_request, redis_clean):
    genre_id = genres_data[0].id
    response = await make_get_request(f'/genres/{genre_id}')

    assert response.status == HTTPStatus.OK
    assert response.body == genres_data[0].dict()

    response = await make_get_request('/genres/00000000-0000-0000-0000-000000000')
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_genre_list_pagination(genres_data, genres_fill_data, make_get_request, redis_clean):
    page_size = 3
    last_page_number = ceil(len(genres_data) / page_size)
    last_page_size = len(genres_data) % page_size

    # First page
    response = await make_get_request('/genres', params={'size': page_size})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] is None
    assert response.body['next'] == 2
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == page_size

    # Second page
    response = await make_get_request('/genres', params={'size': page_size, 'page': 2})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] == 1
    assert response.body['next'] == 3
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == page_size

    # Last page
    response = await make_get_request('/genres',
                                      params={'size': page_size, 'page': last_page_number})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] == last_page_number - 1
    assert response.body['next'] is None
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == last_page_size


@pytest.mark.asyncio
async def test_genre_list_pagination_incorrect_pages(genres_data, genres_fill_data, make_get_request, redis_clean):
    page_size = 3
    last_page_number = ceil(len(genres_data) / page_size)

    # The page number less than 1
    response = await make_get_request('/genres', params={'size': page_size, 'page': -1})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    # The page number more than last page number
    response = await make_get_request('/genres', params={'size': page_size, 'page': last_page_number + 1})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 0


@pytest.mark.asyncio
async def test_genre_list_sort(genres_data, genres_fill_data, make_get_request, redis_clean):
    sorted_data = sorted(genres_data, key=lambda g: g.name)

    response = await make_get_request('/genres', params={'sort': 'name:asc'})
    assert response.body['data'][0] == sorted_data[0].dict()
    assert response.body['data'][1] == sorted_data[1].dict()

    response = await make_get_request('/genres', params={'sort': 'name:desc'})
    assert response.body['data'][0] == sorted_data[-1].dict()
    assert response.body['data'][1] == sorted_data[-2].dict()
