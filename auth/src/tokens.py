import uuid
from datetime import datetime, timedelta
from enum import Enum

import jwt
from database.db_models import User
from jwt.exceptions import PyJWTError
from settings import api_settings
from storage_token import get_storage_tokens

storage = get_storage_tokens()


class TokenType(str, Enum):
    access_token = 'access_token'
    refresh_token = 'refresh_token'


def generate_token(user: User, token_type: TokenType, algorithms: list[str] | None = 'HS256') -> bytes:
    """
    Generate JWT-token.

    :param user: the user the token is generated for.
    :param token_type: the token type (is used to define secret key and token lifetime).
    :param algorithms: the algorithms to encrypt token.
    :return: JWT-token.
    """
    if token_type == TokenType.access_token:
        lifetime_hours = api_settings.access_token_lifetime_hours
        secret = api_settings.access_token_secret_key
    elif token_type == TokenType.refresh_token:
        lifetime_hours = api_settings.refresh_token_lifetime_hours
        secret = api_settings.refresh_token_secret_key
    else:
        raise ValueError('Unknown token type')

    lat = datetime.utcnow()
    exp = lat + timedelta(hours=lifetime_hours)
    jti = str(uuid.uuid4())
    payload = {
        'user': str(user.id),
        'roles': [str(r.name) for r in user.roles],
        'lat': int(datetime.timestamp(lat)),
        'exp': int(datetime.timestamp(exp)),
        'jti': jti
    }

    token = jwt.encode(payload, secret, algorithms)
    return token


def decode_token(token: bytes, token_type: TokenType, algorithms: list[str] | None = 'HS256') -> dict:
    """
    Decode JWT-token.

    :param token: the JWT-token.
    :param token_type: the token type (is used to define secret key).
    :param algorithms algorithms to decode.
    :return: decoded token payload part.
    """
    if token_type == TokenType.access_token:
        secret = api_settings.access_token_secret_key
    elif token_type == TokenType.refresh_token:
        secret = api_settings.refresh_token_secret_key
    else:
        raise ValueError('Unknown token type')
    payload = jwt.decode(token, secret, algorithms)
    return payload


def validate_auth_header(auth_header: str, token_type: TokenType = TokenType.access_token) -> dict:
    """
    Validate the 'Authorization' HTTP header passed as a parameter.

    :param auth_header: header value (it is expected 'Bearer <Token>' format).
    :param token_type: token type.
    :return: the decoded token payload part in case of success, the dict with 'error' key otherwise.
    """
    try:
        refresh_token = auth_header.split()[1].encode('utf8')
        payload = decode_token(refresh_token, token_type)
        if storage.check_token_is_compromised(payload['jti']):
            return {'error': 'The token has been compromised. Please, try login again.'}
    except IndexError:
        return {'error': 'Authorization header is wrong. It must be like "Bearer <token>".'}
    except PyJWTError as e:
        return {'error': f'Token error: {str(e)}'}
    return {'payload': payload}
