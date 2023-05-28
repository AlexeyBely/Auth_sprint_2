from functools import wraps
from http import HTTPStatus
from typing import Iterable

from flask import request

import messages
from database.db_models import User
from storage_token import get_storage_tokens
from tokens import TokenType, validate_auth_header

storage = get_storage_tokens()


def authorization(token_type: TokenType = TokenType.access_token, safe_methods: Iterable | None = None,
                  allowed_user_roles: Iterable | str = '__all__'):
    """
    The function checks the validity of the refresh_token and the user.

    :param token_type: a token type to check authorization.
    :param safe_methods: a list of HTTP-methods to skip authorization.
    :param allowed_user_roles: List of user roles that are allowed to use the method. If it has string value '__all__',
            then the validation is skipped. The 'superuser' role is not restricted. Note, safe_methods parameter has
            higher priority, it means that if request method is in safe methods, user roles are not validated.
    :return auth_data: the dict {'user': User, 'payload': list} (payload list fields, see tokens.generate_token)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if (isinstance(allowed_user_roles, str) and allowed_user_roles != '__all__'
                    or not isinstance(allowed_user_roles, Iterable)):
                raise ValueError(messages.ERR_WRONG_VALUE.format(allowed_user_roles))
            elif len(allowed_user_roles) == 0:
                raise ValueError(messages.ERR_EMPTY_VALUE.format(allowed_user_roles))

            if safe_methods and request.method in safe_methods:
                return func(*args, **kwargs)

            header = request.headers.get('Authorization', "Bearer <Token>")
            validated = validate_auth_header(header, token_type)
            if 'error' in validated:
                return validated, HTTPStatus.UNAUTHORIZED

            user = User.query.filter_by(id=validated.get('payload').get('user')).first()
            if not user:
                return {'error': messages.ERR_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

            if token_type is TokenType.refresh_token:
                refresh_token = header.split()[1].encode('utf8')
                if storage.check_refresh_token_is_valid(user.id, refresh_token) is False:
                    return {'error': messages.ERR_REFRESH_TOKEN_NOT_EXIST}, HTTPStatus.UNAUTHORIZED
            auth_data = {'user': user, 'payload': validated['payload']}

            if allowed_user_roles != '__all__':
                user_roles = auth_data.get('payload').get('roles', [])
                if not user_roles or 'superuser' not in user_roles and all([r not in allowed_user_roles for r in user_roles]):
                    return {'error': messages.ERR_ACTION_NOT_ALLOWED}, HTTPStatus.FORBIDDEN
            result = func(*args, **kwargs, auth_data=auth_data)
            return result
        return wrapper
    return decorator
