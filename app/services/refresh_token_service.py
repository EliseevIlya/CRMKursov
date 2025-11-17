from app.config import settings
from app.redis_client import redis_client_init
from datetime import timedelta


class RefreshTokenStore:
    PREFIX = settings.REDIS_REFRESH_PREFIX  # e.g. "refresh:"

    @staticmethod
    async def save(user_id: int, jti: str, token: str, ttl_days: int = None):
        ttl = 60 * 60 * 24 * (ttl_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
        key = f"{RefreshTokenStore.PREFIX}{user_id}:{jti}"
        await redis_client_init.set_value(key, token, ttl)

    @staticmethod
    async def exists(user_id: int, jti: str) -> bool:
        key = f"{RefreshTokenStore.PREFIX}{user_id}:{jti}"
        val = await redis_client_init.get_value(key)
        return bool(val)

    @staticmethod
    async def delete(user_id: int, jti: str):
        key = f"{RefreshTokenStore.PREFIX}{user_id}:{jti}"
        await redis_client_init.delete_key(key)

    @staticmethod
    async def revoke_all_for_user(user_id: int):
        pattern = f"{RefreshTokenStore.PREFIX}{user_id}:*"
        await redis_client_init.delete_keys_by_prefix(f"{RefreshTokenStore.PREFIX}{user_id}:")
