from http import HTTPStatus

from flask import Blueprint, abort, make_response, request
from flask.views import MethodView
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

import messages
from .auth import authorization
from database.db import db
from database.db_models import User, UserRole
from schemas.role_schemas import (role_detail_schema, role_list_schema, role_update_schema, 
                                  user_provide_role_schema, query_user_id_schema)
from utils.tracer import trace


app_role = Blueprint('role_routes', __name__)


class ItemAPI(MethodView):
    def __init__(self, session, model, response_schema, update_schema):
        self.session = session
        self.model = model
        self.response_schema = response_schema
        self.update_schema = update_schema

    def _get_item(self, id):
        item = self.model.query.get(id)
        if not item:
            response = make_response({'error': 'Not found'}, HTTPStatus.NOT_FOUND)
            abort(response)
        return item

    def get(self, id):
        """
        ---
        summary: Получить роль по ID
        parameters:
            - in: path
              schema: InputUuidSchema
        responses:
            '200':
                description: Роль пользователя
                content:
                    application/json:
                        schema: UserRoleSchema
            '404':
                description: Роли с указанным ID не существует
        tags:
            - roles
        """
        item = self._get_item(id)
        return self.response_schema.dump(item)

    @authorization(allowed_user_roles=['superuser'])
    def patch(self, id, *args, **kwargs):
        """
        ---
        summary: Обновление информации о роли
        parameters:
            - in: path
              schema: InputUuidSchema
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: UserRoleUpdateSchema
        responses:
            '200':
                description: Роль обновлена
                content:
                    application/json:
                        schema: UserRoleSchema
            '400':
                description: Не переданы данные для обновления или они некорректны.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '409':
                description: Роль с таким названием уже существует
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - roles
        """
        try:
            item = self._get_item(id)
            data = self.update_schema.load(request.json)
            item.name = data['name']
            self.session.add(item)
            self.session.commit()
        except BadRequest:
            return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
        except IntegrityError as e:
            return {'error': e.orig.args}, HTTPStatus.CONFLICT
        except ValidationError as e:
            return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
        return self.response_schema.dump(item), HTTPStatus.OK

    @authorization(allowed_user_roles=['superuser'])
    def delete(self, id, *args, **kwargs):
        """
        ---
        summary: Удаление роли
        parameters:
            - in: path
              schema: InputUuidSchema
        security:
            - AccessToken: []
        responses:
            '200':
                description: Роль успешно удалена
                content:
                    application/json:
                        schema: OutputDetailSchema
            '404':
                description: Роль с указанным ID не найдена
        tags:
            - roles
        """
        item = self._get_item(id)
        self.session.delete(item)
        self.session.commit()
        return {'detail': 'Deleted'}, HTTPStatus.NO_CONTENT


class GroupAPI(MethodView):
    def __init__(self, session, model, response_schema, create_schema):
        self.session = session
        self.model = model
        self.response_schema = response_schema
        self.create_schema = create_schema

    @trace
    def get(self):
        """
        ---
        summary: Получить список пользовательских ролей
        responses:
            '200':
                description: Список пользовательских ролей
                content:
                    application/json:
                        schema:
                            type: array
                            items: UserRoleSchema
        tags:
            - roles
        """
        items = self.model.query.all()
        return self.response_schema.dump(items), HTTPStatus.OK

    @authorization(allowed_user_roles=['superuser'])
    def post(self, *args, **kwargs):
        """
        ---
        summary: Создание новой роли
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: UserRoleUpdateSchema
        responses:
            '201':
                description: Роль успешно создана
                content:
                    application/json:
                        schema: UserRoleSchema
            '400':
                description: Не переданы данные для обновления или они некорректны.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '409':
                description: Роль с таким названием уже существует
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - roles
        """
        try:
            data = role_detail_schema.load(request.json)
            role = self.model(**data)
            self.session.add(role)
            self.session.commit()
        except BadRequest:
            return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
        except IntegrityError as e:
            return {'error': e.orig.args}, HTTPStatus.CONFLICT
        except ValidationError as e:
            return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
        return role_detail_schema.dump(role), HTTPStatus.CREATED


role_item = ItemAPI.as_view('roles-item', db.session, UserRole, role_detail_schema, role_update_schema)
app_role.add_url_rule('/auth/roles/<id>/', view_func=role_item)

role_group = GroupAPI.as_view('roles-group', db.session, UserRole, role_list_schema, role_detail_schema)
app_role.add_url_rule('/auth/roles/', view_func=role_group)


@app_role.route('/auth/roles/provide/', methods=['POST'])
@authorization(allowed_user_roles=['superuser'])
def user_provide_role(*args, **kwargs):
    """
    ---
    post:
        summary: Назначить роль пользователю
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: UserProvideRoleSchema
        responses:
            '200':
                description: Роль назначена успешно
                content:
                    application/json:
                        schema: OutputDetailSchema
            '400':
                description: Не переданы данные для обновления или они некорректны.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '404':
                description: Пользователь или роль не найдены
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - roles
    """
    try:
        json_data = request.get_json()
        data = user_provide_role_schema.load(json_data)
        user = User.query.get(data.get('user_id', ''))
        if not user:
            return {'error': messages.ERR_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
        role = UserRole.query.get(data.get('role_id', ''))
        if not role:
            return {'error': messages.ERR_USER_ROLE_NOT_FOUND}, HTTPStatus.NOT_FOUND
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    return {'detail': messages.ROLE_PROVIDED}, HTTPStatus.OK


@app_role.route('/auth/roles/revoke/', methods=['POST'])
@authorization(allowed_user_roles=['superuser'])
def user_revoke_role(*args, **kwargs):
    """
    ---
    post:
        summary: Отозвать роль у пользователя
        security:
            - AccessToken: []
        requestBody:
            content:
                application/json:
                    schema: UserProvideRoleSchema
        responses:
            '200':
                description: Роль отозвана успешно
                content:
                    application/json:
                        schema: OutputDetailSchema
            '400':
                description: Не переданы данные для обновления или они некорректны.
                content:
                    application/json:
                        schema: OutputErrorSchema
            '404':
                description: Пользователь или роль не найдены
                content:
                    application/json:
                        schema: OutputErrorSchema
            '422':
                description: Ошибка валидации данных.
                content:
                    application/json:
                        schema: OutputErrorSchema
        tags:
            - roles
    """
    try:
        json_data = request.get_json()
        data = user_provide_role_schema.load(json_data)
        user = User.query.get_or_404(data.get('user_id', ''))
        role = UserRole.query.get_or_404(data.get('role_id', ''))
        user.roles.remove(role)
        db.session.commit()
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except ValueError:
        return {'error': messages.ERR_USER_ROLE_VALUE_ERROR}
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    return {'detail': messages.ROLE_REVOKED}, HTTPStatus.OK
