import json

import redis.asyncio as redis

from app.config import get_redis_url


class RedisClient:
    def __init__(self, url: str = None):
        self._url = url or get_redis_url()
        self._redis: redis.Redis | None = None

    async def connect(self):
        """Подключение к Redis"""
        if self._redis is None:
            self._redis = redis.from_url(self._url, decode_responses=True)

    async def close(self):
        """Закрыть соединение"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def set_json(self, key: str, value: dict, ttl: int | None = None):
        """Сохранить JSON с TTL"""
        if self._redis is None:
            raise RuntimeError("Redis клиент не инициализирован")
        await self._redis.set(key, json.dumps(value), ex=ttl)

    async def get_json(self, key: str) -> dict | None:
        """Прочитать JSON"""
        if self._redis is None:
            raise RuntimeError("Redis клиент не инициализирован")
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set_value(self, key: str, value: str, ttl: int | None = None):
        """Сохранить строку"""
        if self._redis is None:
            raise RuntimeError("Redis клиент не инициализирован")
        await self._redis.set(key, value, ex=ttl)

    async def get_value(self, key: str) -> str | None:
        """Прочитать строку"""
        if self._redis is None:
            raise RuntimeError("Redis клиент не инициализирован")
        return await self._redis.get(key)

    async def delete_key(self, key: str):
        """Удаляет ключ из Redis."""
        if self._redis:
            await self._redis.delete(key)

    async def delete_keys_by_prefix(self, prefix: str):
        """Удаляет все ключи, начинающиеся с указанного префикса."""
        if self._redis:
            keys = await self._redis.keys(prefix + "*")
            if keys:
                await self._redis.delete(*keys)

    async def delete_all_keys(self):
        """Очищает текущую базу данных Redis."""
        if self._redis:
            await self._redis.flushdb()

    def get_redis_client(self) -> redis.Redis:
        """Возвращает объект клиента Redis."""
        if self._redis is None:
            raise RuntimeError("Redis клиент не инициализирован")
        return self._redis

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


redis_client_init = RedisClient()
