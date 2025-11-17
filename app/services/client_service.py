from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories.postgres.client_repo import ClientRepo
from app.repositories.postgres.subscription_repo import SubscriptionRepo
from app.repositories.redis.active_client_cache import ActiveClientCache
from app.db.models import Client, Subscription
from app.schemas.postgres import ClientCreate, ClientUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=[settings.CRYPT_SCHEME], deprecated="auto")


class ClientService:
    def __init__(self, session: AsyncSession):
        self.clients = ClientRepo(session)
        self.subs = SubscriptionRepo(session)
        self.cache = ActiveClientCache()

    async def get(self, client_id: int):
        cached = await self.cache.get(client_id)
        if cached:
            return cached
        client = await self.clients.get(client_id)
        if not client:
            return None
        active_sub = await self.subs.get_active_by_client(client_id)
        payload = {
            "id": client.id,
            "email": client.email,
            "full_name": client.full_name,
            "phone": client.phone,
            "is_active": client.is_active,
            "has_active_subscription": bool(active_sub)
        }
        await self.cache.set(client.id, payload)
        return payload

    async def list(self, offset: int = 0, limit: int = 50):
        return await self.clients.list(offset, limit)

    async def create(self, data: ClientCreate):
        hashed = pwd_context.hash(data.password) if data.password else None
        client = Client(email=data.email, password_hash=hashed, full_name=data.full_name, phone=data.phone,
                        is_active=data.is_active)
        created = await self.clients.create(client)
        # set cache
        await self.cache.set(created.id, {"id": created.id, "email": created.email, "full_name": created.full_name})
        return created

    async def update(self, client_id: int, data: ClientUpdate):
        client = await self.clients.get(client_id)
        if not client:
            return None
        updated = await self.clients.update(client, **data.dict(exclude_unset=True))
        await self.cache.set(updated.id, {"id": updated.id, "email": updated.email, "full_name": updated.full_name})
        return updated
