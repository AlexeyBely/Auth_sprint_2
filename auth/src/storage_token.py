from uuid import UUID

from database.db import redis_db
from redis import Redis
from settings import api_settings as _as


class StorageTokens():
    """Saving and retrieving tokens in Redis database."""
    def __init__(self, redis: Redis):
        self.redis = redis

    def save_access_refresh_tokens(self, id: UUID, access_token: str,
                                   refresh_token: str) -> None:
        user_id = str(id)
        self._save_data(f'accessToken_{user_id}', access_token, True)
        self._save_data(f'refreshToken_{user_id}', refresh_token, False)

    def set_token_to_compromised(self, jti: str, id: UUID | None = None) -> None:
        self._save_data(f'jtiBlock_{jti}', '', False)
        if id is not None:
            user_id = str(id)
            self.redis.delete(f'accessToken_{user_id}')
            self.redis.delete(f'refreshToken_{user_id}')

    def check_token_is_compromised(self, jti: str) -> bool:
        load_jti = self._retrieve_data(f'jtiBlock_{jti}')
        return load_jti is not None

    def check_refresh_token_is_valid(self, user_id: UUID, refresh_token: str) -> bool:
        id = str(user_id)
        load_jwt = self._retrieve_data(f'refreshToken_{id}')
        return load_jwt == refresh_token

    def get_refresh_token(self, user_id: UUID) -> str:
        id = str(user_id)
        load_jwt = self._retrieve_data(f'refreshToken_{id}')
        return load_jwt

    def _save_data(self, key: str, data: str, is_access: bool) -> None:
        if is_access is True:
            expire_time = _as.access_token_lifetime_hours * 60
        else:
            expire_time = _as.refresh_token_lifetime_hours * 60
        self.redis.set(key, data, ex=expire_time)

    def _retrieve_data(self, key: str) -> str | None:
        return self.redis.get(key)


storage_tokens = StorageTokens(redis_db)


def get_storage_tokens() -> StorageTokens:
    return storage_tokens
