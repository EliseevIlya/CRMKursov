from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.postgres.visit_repo import VisitRepo
from app.repositories.postgres.subscription_repo import SubscriptionRepo
from app.repositories.redis.active_client_cache import ActiveClientCache
from app.db.models import Visit
from app.schemas.postgres import VisitCreate
from datetime import datetime


class VisitService:
    def __init__(self, session: AsyncSession):
        self.repo = VisitRepo(session)
        self.subs = SubscriptionRepo(session)
        self.cache = ActiveClientCache()

    async def list(self, offset: int = 0, limit: int = 50):
        return await self.repo.list(offset, limit)

    async def create(self, data: VisitCreate):
        # проверка подписки
        active_sub = await self.subs.get_active_by_client(data.client_id)
        if not active_sub:
            raise ValueError("Client has no active subscription")

        visit_time = data.visit_time or datetime.utcnow()
        visit = Visit(client_id=data.client_id, trainer_id=data.trainer_id, visit_time=visit_time)
        created = await self.repo.create(visit)

        # поместим клиента в кэш active
        await self.cache.set(data.client_id, {"client_id": data.client_id, "last_visit": visit_time.isoformat()},
                             ttl=60 * 60)
        return created
