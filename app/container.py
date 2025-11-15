import aiohttp

from app.database import init_db
from app.mongo import init_mongo
from app.redis_client import redis_client_init


class Container:
    def __init__(self):
        self.session_http: aiohttp.ClientSession | None = None


    async def connect(self):
        """Подключить все ресурсы"""
        await redis_client_init.connect()
        await init_mongo()
        await init_db()

        self.session_http = aiohttp.ClientSession()


    async def close(self):
        """Закрыть все ресурсы"""
        await redis_client_init.close()
        if self.session_http:
            await self.session_http.close()
            self.session_http = None




global_container = Container()
