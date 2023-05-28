from http import HTTPStatus

from flask import Flask, jsonify, make_response
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address

from settings import api_settings


def default_error_responder(request_limit: RequestLimit):
    return make_response(jsonify({'error': f'Too many requests'}), HTTPStatus.TOO_MANY_REQUESTS)


def get_limiter(app: Flask):
    return Limiter(
        app,
        key_func=get_remote_address,
        storage_uri=f'redis://{api_settings.auth_redis_host}:{api_settings.auth_redis_port}',
        default_limits=api_settings.auth_requests_limits.split(','),
        strategy='fixed-window',
        on_breach=default_error_responder
    )
