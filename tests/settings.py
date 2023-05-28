from pydantic import BaseSettings, root_validator


class Settings(BaseSettings):
    es_host: str
    es_port: int
    es_url: str | None = None
    fastapi_host: str
    fastapi_port: int
    service_url: str | None = None
    redis_host: str
    redis_port: int

    @root_validator
    def compute_service_url(cls, values):
        if values.get('service_url', None) is None:
            port = values['fastapi_port']
            host = values['fastapi_host']
            values['service_url'] = f"http://{host}:{port}"
        return values

    @root_validator
    def compute_es_url(cls, values):
        if values.get('es_url', None) is None:
            es_host = values.get('es_host')
            es_port = values.get('es_port')
            values['es_url'] = f'http://{es_host}:{es_port}'
        return values


settings = Settings()
