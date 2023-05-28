from http import HTTPStatus
from math import ceil

import pytest


@pytest.mark.asyncio
async def test_person(persons_data, persons_fill_data, make_get_request, redis_clean):
    person_id = persons_data[0].id
    response = await make_get_request(f'/persons/{person_id}')

    assert response.status == HTTPStatus.OK
    assert response.body == persons_data[0].dict(by_alias=True)

    response = await make_get_request('/persons/00000000-0000-0000-0000-000000000')
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_person_list_pagination(persons_data, persons_fill_data, make_get_request, redis_clean):
    # We expected that the persons_data length is at least for 3 pages
    page_size = 3
    last_page_number = ceil(len(persons_data) / page_size)
    last_page_size = len(persons_data) % page_size

    # First page
    response = await make_get_request('/persons', params={'size': page_size})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] is None
    assert response.body['next'] == 2
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == page_size

    # Second page
    response = await make_get_request('/persons', params={'size': page_size, 'page': 2})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] == 1
    assert response.body['next'] == 3
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == page_size

    # Last page
    response = await make_get_request('/persons',
                                      params={'size': page_size, 'page': last_page_number})
    assert response.status == HTTPStatus.OK
    assert response.body['prev'] == last_page_number - 1
    assert response.body['next'] is None
    assert response.body['first'] == 1
    assert response.body['last'] == last_page_number
    assert len(response.body['data']) == last_page_size


@pytest.mark.asyncio
async def test_person_list_pagination_incorrect_pages(persons_data, persons_fill_data, make_get_request, redis_clean):
    page_size = 3
    last_page_number = ceil(len(persons_data) / page_size)

    # The page number less than 1
    response = await make_get_request('/persons', params={'size': page_size, 'page': -1})
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    # The page number more than last page number
    response = await make_get_request('/persons', params={'size': page_size, 'page': last_page_number + 1})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 0


@pytest.mark.asyncio
async def test_person_list_sort(persons_data, persons_fill_data, make_get_request, redis_clean):
    sorted_data = sorted(persons_data, key=lambda p: p.full_name)

    response = await make_get_request('/persons', params={'sort': 'full_name:asc'})
    assert response.body['data'][0] == sorted_data[0].dict(by_alias=True)
    assert response.body['data'][1] == sorted_data[1].dict(by_alias=True)

    response = await make_get_request('/persons', params={'sort': 'full_name:desc'})
    assert response.body['data'][0] == sorted_data[-1].dict(by_alias=True)
    assert response.body['data'][1] == sorted_data[-2].dict(by_alias=True)


@pytest.mark.asyncio
async def test_person_search(persons_data, persons_fill_data, make_get_request, redis_clean):

    response = await make_get_request('/persons/search', params={'query': 'Peter'})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 2

    response = await make_get_request('/persons/search', params={'query': 'Vasily'})
    assert response.status == HTTPStatus.OK
    assert len(response.body['data']) == 0
