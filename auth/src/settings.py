from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'Movies'
    flask_host: str = '127.0.0.1'
    flask_port: int = 5000
    auth_postgres_db: str = 'auth_db'
    auth_postgres_host: str = '127.0.0.1'
    auth_postgres_port: int = 5433
    auth_postgres_user: str = 'auth_admin'
    auth_postgres_password: str = 'auth_admin'
    access_token_secret_key: str = '256-bit-secret-key-1'
    access_token_lifetime_hours: int = 1
    refresh_token_secret_key: str = '256-bit-secret-key-2'
    refresh_token_lifetime_hours: int = 24 * 7
    auth_redis_host: str = '127.0.0.1'
    auth_redis_port: int = 6379
    redirect_uri_yandex: str = 'https://oauth.yandex.ru/'
    redirect_uri_vk: str = 'https://oauth.vk.com/blank.html'
    jaeger_host: str = 'jaeger'
    jaeger_port: int = 6831
    tracer_enable: bool = False
    auth_requests_limits: str = '250/day,50/minute'
    yandex_base_url: str = 'https://oauth.yandex.ru/'
    vk_base_url = 'https://oauth.vk.com/'
    grpc_port: int = 50051


api_settings = Settings()
