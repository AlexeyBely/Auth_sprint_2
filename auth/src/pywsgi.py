from gevent import monkey

monkey.patch_all()

from gevent.pywsgi import WSGIServer

from app import app
from settings import api_settings


http_server = WSGIServer(('', api_settings.flask_port), app)
http_server.serve_forever()
