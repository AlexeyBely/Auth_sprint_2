from typing import Type

import orjson
from aioredis import Redis
from core.config import api_settings
from db.redis import get_redis_sync

from .base_storage import BaseStorage


class RedisStorage(BaseStorage):
    """Saving and retrieving data in Redis database."""
    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_data(self, key: str, data: dict) -> None:
        """Save state to storage."""
        self.__check_redis()
        await self.redis.set(
            key,
            orjson.dumps(data),
            expire=api_settings.redis_cache_expire
        )

    async def retrieve_data(self, key: str) -> dict | None:
        """Load state locally from storage."""
        self.__check_redis()
        data_redis = await self.redis.get(key)
        if not data_redis:
            return None
        return(orjson.loads(data_redis))

    def __check_redis(self) -> None:
        if self.redis is None:
            self.redis = get_redis_sync()


redis_storage = RedisStorage(get_redis_sync())


def get_redis_storage() -> Type[BaseStorage]:
    """interface and cache storage connectivity."""
    return redis_storage
