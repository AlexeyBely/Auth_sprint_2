import socket

from backoff import backoff
from waiting import waiting


DEFAULT_HOST = 'flask'
DEFAULT_PORT = '5000'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@backoff()
def flask_connect(host: str, port: str):
    s.connect((host, int(port)))
    s.close()


if __name__ == '__main__':
    waiting('Flask', flask_connect, default_host=DEFAULT_HOST, default_port=DEFAULT_PORT)
