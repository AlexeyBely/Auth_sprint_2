from http import HTTPStatus
import json

from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest
from flask_sqlalchemy import Pagination
from user_agents import parse

import messages
from .auth import authorization
from database.db import db
from database.db_models import LoginHistory, User, UserDeviceType
from schemas import auth_schemas, history_schemas, user_schemas
from storage_token import get_storage_tokens
from tokens import TokenType, decode_token, generate_token
from utils.tracer import trace


app_auth = Blueprint('auth_routes', __name__)
storage = get_storage_tokens()


@app_auth.route('/auth/signup/', methods=['POST'])
def sign_up():
    """
    ---
    post:
        summary: Регистрация пользователя
        requestBody:
            content:
                application/json:
                    schema: UserSignUpSchema
        responses:
            '200':
                description: Данные пользователя
                content:
                    application/json:
                        schema: UserSchema
        tags:
            - auth
    """
    try:
        json_data = request.get_json()
        data = user_schemas.user_sign_up_schema.load(json_data)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except IntegrityError as e:
        return {'error': e.orig.args}, HTTPStatus.CONFLICT
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    return user_schemas.user_detail_schema.dump(user), HTTPStatus.OK


@trace
@app_auth.route('/auth/login/', methods=['POST'])
def login():
    """
    ---
    post:
        summary: Авторизация пользователя
        requestBody:
            content:
                application/json:
                    schema: UserLoginSchema
        responses:
            '200':
                description: Токены доступа пользователя
                content:
                    application/json:
                        schema: TokensSchema
        tags:
            - auth
    """
    try:
        json_data = request.get_json()
        user_schemas.user_login_schema.load(json_data)
        user = User.query.filter_by(email=json_data.get('email')).first()
        if not user:
            return {'error': messages.ERR_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND
        if not user.check_password(json_data.get('password')):
            return {'error': messages.ERR_WRONG_PASSWORD}, HTTPStatus.UNAUTHORIZED
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    access_token = generate_token(user, TokenType.access_token)
    refresh_token = generate_token(user, TokenType.refresh_token)
    # add tokens to storage
    storage.save_access_refresh_tokens(user.id, access_token, refresh_token)
    # add history
    user_agent = request.headers.get('User-Agent')
    parse_ua = parse(user_agent)
    device_type = UserDeviceType.OTHER
    if (parse_ua.is_mobile | parse_ua.is_tablet) is True:
        device_type = UserDeviceType.MOBILE
    if parse_ua.is_pc is True:
        device_type = UserDeviceType.PS     
    data = {'user_id': user.id,
           'user_agent': user_agent,
           'user_device_type': str(device_type),}
    log = LoginHistory(**data)
    db.session.add(log)
    db.session.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.OK


@app_auth.route('/auth/refresh-token/', methods=['POST'])
@authorization(token_type=TokenType.refresh_token)
def refresh_access_token(auth_data: dict):
    """
    ---
    post:
        summary: Обновление access_token
        security:
            - RefreshToken: []
        responses:
            '200':
                description: Токен доступа access_token
                content:
                    application/json:
                        schema: AccessTokenSchema
        tags:
            - auth
    """
    access_token = generate_token(auth_data['user'], TokenType.access_token)
    return {'access_token': access_token}, HTTPStatus.OK


@app_auth.route('/auth/logout/', methods=['POST'])
@authorization()
def logout(auth_data: dict):
    """
    ---
    post:
        summary: Выход пользователя
        security:
            - AccessToken: []
        responses:
            '200':
                description: Сообщение "Access and refrash tokens revoked"
        tags:
            - auth
    """
    # add tokens to black list
    jti = auth_data['payload']['jti']
    storage.set_token_to_compromised(jti)
    user_id = auth_data['user'].id
    refresh_token = storage.get_refresh_token(user_id)
    jti = decode_token(refresh_token, TokenType.refresh_token)['jti']
    storage.set_token_to_compromised(jti, user_id)
    return {'detail': messages.TOKENS_REVOKED}, HTTPStatus.OK


@app_auth.route('/auth/login-history/', methods=['GET'])
@authorization()
def login_history(auth_data: dict):
    """
    ---
    get:
        summary: Информация о авторизациях пользователя
        parameters:
            - in: query
              schema: QueryHistorySchema
        security:
            - AccessToken: []
        responses:
            '200':
                description: Список дат авторизации
                content:
                    application/json:
                        schema: ItemsHistorySchema
        tags:
            - auth
    """
    try:
        request_data = request.args
        data = history_schemas.query_history_schema.load(request_data)
        page = int(data['page'])
        size = int(data['size'])
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    user_id = auth_data['user'].id
    logs: Pagination = LoginHistory.query.filter_by(user_id=user_id).paginate(page, size, True, 1000)
    items = []
    for item in logs.items:
        items.append(
            {'date': str(item.date),
            'device_type': item.user_device_type,
            'user_agent': item.user_agent}
        )
    result = {
        'items': items,
        'prev_num': logs.prev_num,
        'next_num': logs.next_num,
        'total': logs.total,
    }
    return json.dumps(result), HTTPStatus.OK


@app_auth.route('/auth/tokens/is-in-black-list/', methods=['GET'])
def is_token_compromised():
    """
    ---
    get:
        summary: Проверить, занесен ли токен в список скомпрометированных
        parameters:
            - in: query
              schema: AccessTokenSchema
        responses:
            '200':
                description: Булево значение - скомпрометирован ли токен
                content:
                    application/json:
                        schema: IsTokenCompromisedSchema
        tags:
            - auth
    """
    try:
        request_data = request.args
        data = user_schemas.access_token_schema.load(request_data)
        payload = decode_token(data['access_token'], TokenType.access_token)
        is_compromised = storage.check_token_is_compromised(payload['jti'])
    except BadRequest:
        return {'error': messages.ERR_DATA_INCORRECT}, HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        return e.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    except Exception as e:
        return {'error': str(e)}, HTTPStatus.BAD_REQUEST
    return {'is_compromised': is_compromised}, HTTPStatus.OK
