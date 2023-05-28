import socket

from backoff import backoff
from waiting import waiting


DEFAULT_HOST = 'postgres'
DEFAULT_PORT = '5432'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@backoff()
def postgres_connect(host: str, port: str):
    s.connect((host, int(port)))
    s.close()


if __name__ == '__main__':
    waiting('Postgres', postgres_connect, default_host=DEFAULT_HOST, default_port=DEFAULT_PORT)
