from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.postgres.subscription_repo import SubscriptionRepo
from app.repositories.postgres.client_repo import ClientRepo
from app.db.models import Subscription
from app.schemas.postgres import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.repo = SubscriptionRepo(session)
        self.clients = ClientRepo(session)

    async def get(self, subscription_id: int):
        return await self.repo.get(subscription_id)

    async def get_active_for_client(self, client_id: int):
        return await self.repo.get_active_by_client(client_id)

    async def create(self, data: SubscriptionCreate):
        # optional: validate client exists
        client = await self.clients.get(data.client_id)
        if not client:
            raise ValueError("Client not found")
        s = Subscription(client_id=data.client_id, membership_type_id=data.membership_type_id,
                         start_date=data.start_date, end_date=data.end_date, is_active=data.is_active)
        return await self.repo.create(s)

    async def update(self, subscription_id: int, data: SubscriptionUpdate):
        s = await self.repo.get(subscription_id)
        if not s: return None
        return await self.repo.update(s, **data.dict(exclude_unset=True))
