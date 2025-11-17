from app.redis_client import redis_client_init


class ActiveClientCache:
    PREFIX = "active_client:"

    async def set(self, client_id: int, data: dict, ttl: int = 60 * 30):
        await redis_client_init.set_json(f"{self.PREFIX}{client_id}", data, ttl)

    async def get(self, client_id: int):
        return await redis_client_init.get_json(f"{self.PREFIX}{client_id}")

    async def delete(self, client_id: int):
        await redis_client_init.delete_key(f"{self.PREFIX}{client_id}")

    async def keys(self, pattern: str = "*"):
        # возвращает список ключей active_client:*
        if redis_client_init.get_redis_client():
            return await redis_client_init.get_redis_client().keys(f"{self.PREFIX}{pattern}")
        return []
