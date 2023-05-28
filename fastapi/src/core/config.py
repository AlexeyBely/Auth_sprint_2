from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings, Field


logging_config.dictConfig(LOGGING)


class ApiSettings(BaseSettings):
    project_name: str = 'Movies'
    redis_host: str = 'redis'
    redis_port: int = 6379
    redis_cache_expire: int = 300
    elastic_host: str = Field('es', env='ES_HOST')
    elastic_port: int = Field(9200, env='ES_PORT')
    default_response_page_size: int = 20
    max_page_size: int = 100
    access_token_secret_key: str
    token_algoritm: str = 'HS256'
    check_token_is_compromised_url: str = 'http://auth:5000/auth/tokens/is-in-black-list/'


api_settings = ApiSettings()
