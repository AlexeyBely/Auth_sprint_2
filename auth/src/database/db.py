from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

from settings import api_settings as _as


db = SQLAlchemy()

redis_db = Redis(host=_as.auth_redis_host,
                 port=_as.auth_redis_port,
                 db=0)


def init_db(app: Flask):
    db.init_app(app)
