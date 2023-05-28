import aioredis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, films, genres, persons
from core.config import api_settings
from db import db_connector, elastic, redis


app = FastAPI(
    title=f'Сервис {api_settings.project_name}',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description='Информация о фильмах, жанрах и людях, участвовавших в создании кинопроизведения',
    version='1.0.1'
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        (api_settings.redis_host, api_settings.redis_port), minsize=10, maxsize=20)
    db_connector.db_connector = elastic.ElasticSearchConnector(
        host=api_settings.elastic_host,
        port=api_settings.elastic_port,
    )


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await db_connector.db_connector.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
