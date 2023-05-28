import asyncio
from dataclasses import dataclass
import uuid

import aiohttp
import aioredis
import pytest
from multidict import CIMultiDictProxy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .settings import settings

pytest_plugins = ('tests.fixtures.user',
                  'tests.fixtures.roles',)


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
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
async def redis():
    redis = await aioredis.create_redis_pool(
        (settings.redis_host, settings.redis_port),
        minsize=10,
        maxsize=20
    )
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope='function')
async def redis_clean(redis):
    redis.flushall()


@pytest.fixture(scope='session')
def sqlalchemy_session():
    engine = create_engine(
        f'postgresql://{settings.auth_postgres_user}:{settings.auth_postgres_password}'
        f'@{settings.auth_postgres_host}:{settings.auth_postgres_port}/{settings.auth_postgres_db}',
        echo=False
    )
    session = Session(engine)

    yield session


@pytest.fixture
def make_request(session):
    async def inner(uri: str,
                    method: str = 'GET',
                    params: dict | None = None,
                    headers: dict | None = None,
                    body: dict | None = None) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        body = body or {}
        url = settings.service_url + uri

        #add X-Request-Id
        request_id = str(uuid.uuid4())
        headers['X-Request-Id'] = request_id

        if method.upper() == 'GET':
            session_method = session.get
        elif method.upper() == 'POST':
            session_method = session.post
        elif method.upper() == 'PATCH':
            session_method = session.patch
        elif method.upper() == 'DELETE':
            session_method = session.delete
        else:
            raise ValueError('Unknown method')
        async with session_method(url, params=params, headers=headers, json=body) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner
