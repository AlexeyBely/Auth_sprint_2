from redis import Redis

from backoff import backoff
from waiting import waiting


DEFAULT_HOST = 'redis'
DEFAULT_PORT = '6379'


@backoff()
def ping_redis(host, port):
    redis = Redis(host=host, port=int(port), socket_connect_timeout=1)
    if not redis.ping():
        redis.close()
        raise ConnectionError('Unable to connect the Redis service')


if __name__ == '__main__':
    waiting('Redis', ping_redis, default_host=DEFAULT_HOST, default_port=DEFAULT_PORT)
