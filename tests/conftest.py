import asyncio
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import settings
from .testdata.models_data import Film, FilmPerson, Genre, Person


@pytest.fixture
def event_loop():
    yield asyncio.get_event_loop()


def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=settings.es_url)
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
async def redis():
    redis = await aioredis.create_redis_pool((settings.redis_host, settings.redis_port), minsize=10, maxsize=20)
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope='function')
async def redis_clean(redis):
    redis.flushall()


@pytest.fixture(scope='session')
async def create_movies_index(es_client):
    with open('/tests/testdata/movies_schema.json') as f:
        schema = f.read()

    await es_client.indices.create(index='movies', body=schema)

    yield es_client
    await es_client.indices.delete(index='movies')


@pytest.fixture(scope='session')
async def create_persons_index(es_client):
    with open('/tests/testdata/persons_schema.json') as f:
        schema = f.read()

    await es_client.indices.create(index='persons', body=schema)

    yield es_client
    await es_client.indices.delete(index='persons')


@pytest.fixture(scope='session')
async def create_genres_index(es_client):
    with open('/tests/testdata/genres_schema.json') as f:
        schema = f.read()

    await es_client.indices.create(index='genres', body=schema)

    yield es_client
    await es_client.indices.delete(index='genres')


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = settings.service_url + '/api/v1' + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


# fixture for model Film
@pytest.fixture(scope='session')
def films_data():
    data = []
    # we expect at least 10 values to test pagination
    genre_names = ['comedy', 'drama', 'fantasy']
    genre_names_sets = ['comedy', 'drama', 'alpha']
    director_names = ['Woody Allen', 'Tim Burton', 'Spike Lee']
    actors_full_names = ['Tom Hanks', 'Al Pacino', 'Johnny Depp']
    writers_full_names = ['Robert Towne', 'Woody Allen', 'Nora Ephron']
    titles = ['The Goodfellas', 'Звезда', 'Star',
              'The dark Knight', 'Fight club', 'Inception', 'Forrest Gump',
              'The Matrix', 'Seven samurai', 'Star Wars', 'The Pianist']
    actors = []
    actors_names = ''
    for name in actors_full_names:
        actors_names += f' {name}'
    for name in actors_full_names:
        person_id = uuid4()
        actor = FilmPerson(id=str(person_id), name=name)
        actors.append(actor)
    writers = []
    for name in writers_full_names:
        person_id = uuid4()
        writer = FilmPerson(id=str(person_id), name=name)
        writers.append(writer)
        rating = 0.0
    for title in titles:
        film_id = uuid4()
        rating += 0.5
        film = Film(
            id=str(film_id),
            imdb_rating=rating,
            genre=list(genre_names_sets) if (rating == 2) | (rating == 4) else list(genre_names),
            title=title,
            description=f'Some description of {title}',
            director=list(director_names),
            actors=actors,
            writers=writers,
            actors_names=actors_names,
            writers_names=list(writers_full_names)
        )
        data.append(film)
    return data


@pytest.fixture(scope='session')
async def films_fill_data(es_client, create_movies_index, films_data):
    query_data = []
    line_header = '{{"index": {{"_index": "movies", "_id": "{}"}}}}\n'
    for film in films_data:
        odd = line_header.format(film.id)
        even = film.json()
        query_data.append(f'{odd}{even}\n')
    await es_client.bulk(
        index='movies',
        body=''.join(query_data),
        refresh='wait_for',
    )


# fixture for model Genre
@pytest.fixture(scope='session')
def genres_data():
    data = []
    # we expect at least 10 values to test pagination
    genre_names = ('omega', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa')
    for name in genre_names:
        genre_id = uuid4()
        genre = Genre(
            id=str(genre_id),
            name=name,
            description=f'Some description of {name}',
        )
        data.append(genre)
    return data


@pytest.fixture(scope='session')
async def genres_fill_data(es_client, create_genres_index, genres_data):
    query_data = []
    line_header = '{{"index": {{"_index": "genres", "_id": "{}"}}}}\n'
    for genre in genres_data:
        odd = line_header.format(genre.id)
        even = genre.json()
        query_data.append(f'{odd}{even}\n')
    await es_client.bulk(
        index='genres',
        body=''.join(query_data),
        refresh='wait_for',
    )


# fixture for model Person
@pytest.fixture(scope='session')
def persons_data():
    data = []
    names = ('Zoe Tate', 'Aimee Peters', 'Alberto Ramos', 'Alexis Werner', 'Cannon Lin', 'Eugene Ibarra',
             'Giuliana Hendricks', 'Jaiden Lang', 'Judah Beard', 'Peter Lara', 'Yair Potts', )
    for name in names:
        person_id = str(uuid4())
        person = Person(id=person_id, name=name)
        data.append(person)
    return data


@pytest.fixture(scope='session')
async def persons_fill_data(es_client, create_persons_index, persons_data):
    query_data = []
    line_header = '{{"index": {{"_index": "persons", "_id": "{}"}}}}\n'
    for person in persons_data:
        odd = line_header.format(person.id)
        even = person.json()
        query_data.append(f'{odd}{even}\n')
    await es_client.bulk(
        index='persons',
        body=''.join(query_data),
        refresh='wait_for',
    )
