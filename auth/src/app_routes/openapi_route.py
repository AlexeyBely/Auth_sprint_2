from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_swagger_ui import get_swaggerui_blueprint


SWAGGER_URL = '/auth/docs'
API_URL = '/auth/swagger'


def create_tags(spec):
    """ Создаем теги.

    :param spec: объект APISpec для сохранения тегов
    """
    tags = [{'name': 'user', 'description': 'Пользователи'},
            {'name': 'auth', 'description': 'Авторизация пользователей'},
            {'name': 'roles', 'description': 'Пользовательские роли'},
            {'name': 'login_oauth', 'description': 'Авторизация через сторонние сервисы'},]

    for tag in tags:
        spec.tag(tag)


def create_security_scheme(spec):
    """ Создаем теги."""

    bearer_auth_scheme = {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}
    spec.components.security_scheme("AccessToken", bearer_auth_scheme)
    spec.components.security_scheme("RefreshToken", bearer_auth_scheme)


def load_docstrings(spec, app):
    """ Загружаем описание API.

    :param spec: объект APISpec, куда загружаем описание функций
    :param app: экземпляр Flask приложения, откуда берем описание функций
    """
    for fn_name in app.view_functions:
        if fn_name == 'static':
            continue
        view_fn = app.view_functions[fn_name]
        spec.path(view=view_fn)


def get_apispec(app):
    """ Формируем объект APISpec.

    :param app: объект Flask приложения
    """
    spec = APISpec(
        title="Сервис авторизации",
        version="1.0.0",
        openapi_version="3.0.3",
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )

    create_tags(spec)
    create_security_scheme(spec)

    load_docstrings(spec, app)

    return spec


swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Сервис авторизации'
    }
)
