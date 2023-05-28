from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, request
from flask.views import MethodView
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

import messages
from .auth import authorization
from database.db import db
from database.db_models import User, LoginHistory, ResourceOauth
from schemas.oauth_schemas import (code_confirmation_schema, resource_oauth_schema,
                                   resource_oauth_list_schema, resource_modifed_schema,
                                   resource_schema)
from storage_token import get_storage_tokens
from services.oauth_service import get_oauth_login_service


app_oauth = Blueprint('oauth_routes', __name__)
storage = get_storage_tokens()
login_service = get_oauth_login_service()
    

class ResourceOauthAPI(MethodView):
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self._init_resources()

    def _init_resources(self):
        name_resources = ('yandex', 'vk')
        for name in name_resources:
            resource = self.model.query.filter_by(name_resource=name).first()
            if not resource:
                data = {'name_resource': name,
                        'client_id': 'client_id',
                        'client_secret': 'client_secret'}
                resource = self.model(**data)
                self.session.add(resource)
                self.session.commit()

    @authorization(allowed_user_roles=['superuser'])
    def get(self, *args, **kwargs):
        """
        ---
        summary: Информация о ресурсах авторизации
        security:
            - AccessToken: []
        responses:
            '200':
                description: Данные ресурсов
                content:
                    application/json:
                        schema: ResourceOauthSchema
        tags:
            - login_oauth
        """
        resources = self.model.query.all()
        return resource_oauth_list_schema.dump(resources), HTTPStatus.OK

    @authorization(allowed_user_roles=['superuser'])
    def patch(self, *args, **kwargs):
        """
        ---
        summary: Обновление информации в ресурсах авторизации
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: ResourceModifedSchema
        responses:
            '200':
                description: данные ресурса
                content:
                    application/json:
                        schema: ResourceOauthSchema
            '400':
                description: Не переданы данные для обновления или они некорректны.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '409':
                description: с таким названием ресурс не существует
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - login_oauth
        """
        try:
            json_data = request.get_json()
            data = resource_modifed_schema.load(json_data)
            name_resource = data['name_resource']
            resource = self.model.query.filter_by(name_resource=name_resource).first()
            if not resource:
                return {'error': messages.NOT_RESOURCE}, HTTPStatus.CONFLICT                
            resource.client_id = data['client_id']
            resource.client_secret = data['client_secret']
            resource.modifed_at = datetime.now()
            self.session.add(resource)
            self.session.commit()
        except BadRequest:
            return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
        except IntegrityError as e:
            return {'error': e.orig.args}, HTTPStatus.CONFLICT
        except ValidationError as e:
            return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
        return resource_oauth_schema.dump(resource), HTTPStatus.OK


resource_oauth = ResourceOauthAPI.as_view('users-resource_oauth',
                                          db.session,
                                          ResourceOauth,)
app_oauth.add_url_rule('/auth/login_oauth/resources/', view_func=resource_oauth)


@app_oauth.route('/auth/login_oauth/client-id/', methods=['GET'])
def get_client_id():
    """
    ---
    get:
        summary: Запррос client_id
        parameters:
            - in: query
              schema: ResourceSchema
        responses:
            '200':
                description: Данные пользователя
                content:
                    application/json:
                        schema: ClientIdSchema
            '409':
                description: Ресурс с таким названием уже существует
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - login_oauth
    """
    try:
        request_data = request.args
        data = resource_schema.load(request_data)
        name_resource = data['name_resource']
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    return login_service.get_client_id(str(name_resource))


@app_oauth.route('/auth/login_oauth/login/', methods=['POST'])
def resource_login():
    """
    ---
    post:
        summary: Регистрация и авторизация пользователя от ресурса
        requestBody:
            content:
                application/json:
                    schema: CodeConfirmationSchema
        responses:
            '200':
                description: Данные пользователя
                content:
                    application/json:
                        schema: TokensSchema
            '400':
                description: Переданы некорректные данные.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - login_oauth
    """
    try:
        json_data = request.get_json()
        data = code_confirmation_schema.load(json_data)
        name_resource = data['name_resource']
        code = data['code']        
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as e:
        return e.messages, HTTPStatus.BAD_REQUEST
    return login_service.resource_login(str(name_resource), code)

