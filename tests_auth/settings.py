from pydantic import BaseSettings, root_validator


class Settings(BaseSettings):
    flask_host: str
    flask_port: int
    service_url: str | None = None
    redis_host: str
    redis_port: int
    auth_postgres_db: str
    auth_postgres_host: str
    auth_postgres_port: int
    auth_postgres_user: str
    auth_postgres_password: str
    auth_superuser_email: str
    auth_superuser_password: str

    @root_validator
    def compute_service_url(cls, values):
        if values.get('service_url', None) is None:
            port = values['flask_port']
            host = values['flask_host']
            values['service_url'] = f"http://{host}:{port}"
        return values


settings = Settings()
