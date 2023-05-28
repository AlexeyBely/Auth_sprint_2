from uuid import uuid4

import pytest

from ..testdata.models_data import Film


@pytest.fixture(scope='session')
async def films_fill_data_added(es_client, create_movies_index):
    film_id = uuid4()
    film_data = Film(
        id=str(film_id),
        imdb_rating=9,
        genre=['drama'],
        title='My film',
        description='New film',
        director=['Woody Allen', 'Tim Burton'],
        actors=[],
        writers=[],
        actors_names='',
        writers_names=[],
    )
    line_header = '{{"index": {{"_index": "movies", "_id": "{}"}}}}\n'
    odd = line_header.format(film_data.id)
    even = film_data.json()
    query_data = []
    query_data.append(f'{odd}{even}\n')
    await es_client.bulk(
        index='movies',
        body=''.join(query_data),
        refresh='wait_for',
    )


@pytest.mark.asyncio
async def test_film_set_cache(films_data, films_fill_data, make_get_request, redis_clean):

    response = await make_get_request('/films')
    assert len(response.body['data']) == 11


@pytest.mark.asyncio
async def test_film_cache_enable(films_data, films_fill_data_added, make_get_request):

    response = await make_get_request('/films')
    assert len(response.body['data']) == 11


@pytest.mark.asyncio
async def test_film_cache_clear(make_get_request, redis_clean):

    response = await make_get_request('/films')
    assert len(response.body['data']) == 12
