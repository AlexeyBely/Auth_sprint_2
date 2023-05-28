import uuid
from http import HTTPStatus

from flask import Blueprint, request
from flask.views import MethodView
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

import messages
from .auth import authorization
from database.db import db
from database.db_models import User
from schemas.user_schemas import (change_password_schema, user_detail_schema, user_list_schema,
                                  user_sign_up_schema, user_with_roles_schema)
from storage_token import get_storage_tokens


app_user = Blueprint('user_routes', __name__)
storage = get_storage_tokens()


class ItemUserAPI(MethodView):
    def __init__(self, session, model, user_detail_schema, user_sign_up_schema):
        self.session = session
        self.model = model
        self.user_detail_schema = user_detail_schema
        self.user_sign_up_schema = user_sign_up_schema

    def _get_user(self, id):
        user = self.model.query.get_or_404(id)
        return user

    def get(self, id: uuid.UUID):
        """
        ---
        summary: Информация о пользователе
        parameters:
            - in: path
              schema: InputUuidSchema
        responses:
            '200':
                description: Данные пользователя
                content:
                    application/json:
                        schema: UserWithRolesSchema
        tags:
            - user
        """
        user = self._get_user(id)
        user_info = user.__dict__
        user_info['user_roles'] = [str(r.name) for r in user.roles]
        return user_with_roles_schema.dump(user_info), HTTPStatus.OK

    @authorization()
    def patch(self, id: uuid.UUID, **kwargs):
        """
        ---
        summary: Обновление информации о пользователе
        parameters:
            - in: path
              schema: InputUuidSchema
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: UserSignUpSchema
        responses:
            '200':
                description: Пользователь обновлен
                content:
                    application/json:
                        schema: UserSchema
            '400':
                description: Не переданы данные для обновления или они некорректны.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '409':
                description: Пользователь с таким названием уже существует
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - user
        """
        try:
            user = self._get_user(id)
            json_data = request.get_json()
            data = self.user_sign_up_schema.load(json_data)
            user.email = data['email']
            user.password = data['password']
            user.full_name = data['full_name']
            self.session.add(user)
            self.session.commit()
        except BadRequest:
            return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
        except IntegrityError as e:
            return {'error': e.orig.args}, HTTPStatus.CONFLICT
        except ValidationError as e:
            return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
        return self.user_detail_schema.dump(user), HTTPStatus.OK

    @authorization()
    def delete(self, id: uuid.UUID, **kwargs):
        """
        ---
        summary: Удаление пользователя
        parameters:
            - in: path
              schema: InputUuidSchema
        security:
            - AccessToken: []
        responses:
            '200':
                description: Сообщение Deleted
            '404':
                description: Пользователь с указанным ID не найден
        tags:
            - user
        """
        user = self._get_user(id)
        self.session.delete(user)
        self.session.commit()
        return {'detail': messages.DELETED}, HTTPStatus.OK


user_item = ItemUserAPI.as_view('users-item',
                                db.session,
                                User,
                                user_detail_schema,
                                user_sign_up_schema)
app_user.add_url_rule('/auth/users/<id>/', view_func=user_item)


@app_user.route('/auth/users/', methods=['GET'])
def user_list(**kwargs):
    """
    ---
    get:
        summary: Информация о пользователях
        responses:
            '200':
                description: Данные пользователей
                content:
                    application/json:
                        schema:
                            type: array
                            items: UserSchema
        tags:
            - user
    """
    users = User.query.all()
    return user_list_schema.dump(users), HTTPStatus.OK


@app_user.route('/auth/users/change-password/', methods=['POST'])
@authorization()
def change_password(auth_data: dict):
    """
    ---
    post:
        summary: Изменение пароля
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: ChangePasswordSchema
        responses:
            '200':
                description: Сообщение "Password was changed successfully!"
        tags:
            - user
    """
    try:
        json_data = request.get_json()
        change_password_schema.load(json_data)
        auth_data['user'].set_password(json_data.get('new_password'))
        db.session.commit()
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    return {'detail': messages.PASSWORD_CHANGED}, HTTPStatus.OK
