import json
import logging
from http import HTTPStatus

from flask import Flask, request
from flask_migrate import Migrate
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from app_routes.auth_routes import app_auth
from app_routes.openapi_route import API_URL, get_apispec, swaggerui_blueprint
from app_routes.role_routes import app_role
from app_routes.user_routes import app_user
from app_routes.oauth_routes import app_oauth
from database.db import db, init_db
from utils.limiter import get_limiter
from schemas import ma
from settings import api_settings as a_s
from utils.tracer import configure_tracer
from utils.cli import cli_bp


logger = logging.getLogger(__name__)

app = Flask(__name__)

db_uri = (f'postgresql://{a_s.auth_postgres_user}:{a_s.auth_postgres_password}'
          f'@{a_s.auth_postgres_host}:{a_s.auth_postgres_port}/{a_s.auth_postgres_db}')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)
ma.init_marshmallow(app)
migrate = Migrate(app, db)

limiter = get_limiter(app)
limiter.init_app(app)


# USER API
app.register_blueprint(app_user)
# ROLES API
app.register_blueprint(app_role)
# AUTH API
app.register_blueprint(app_auth)
# AUTH OAUTH
app.register_blueprint(app_oauth)
# DOCS API
app.register_blueprint(swaggerui_blueprint)
# CLI
app.register_blueprint(cli_bp)


if a_s.tracer_enable:
    configure_tracer()
    FlaskInstrumentor().instrument_app(app)


@app.before_request
def before_request():
    if a_s.tracer_enable:
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            return {'error': '\'X-Request-Id\' header is required'}, HTTPStatus.BAD_REQUEST


@app.route(API_URL)
def create_swagger_spec():
    return json.dumps(get_apispec(app).to_dict())
