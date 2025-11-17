from sqlalchemy import select, and_
from typing import Optional, List
from app.db.models import Subscription
from app.repositories.postgres.base import BaseRepo


class SubscriptionRepo(BaseRepo):
    async def get(self, subscription_id: int) -> Optional[Subscription]:
        q = await self.session.execute(select(Subscription).where(Subscription.id == subscription_id))
        return q.scalars().first()

    async def get_active_by_client(self, client_id: int) -> Optional[Subscription]:
        q = await self.session.execute(select(Subscription).where(
            and_(Subscription.client_id == client_id, Subscription.is_active == True)
        ))
        return q.scalars().first()

    async def list_by_client(self, client_id: int) -> List[Subscription]:
        q = await self.session.execute(select(Subscription).where(Subscription.client_id == client_id))
        return q.scalars().all()

    async def create(self, subscription: Subscription) -> Subscription:
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def update(self, subscription: Subscription, **fields) -> Subscription:
        for k, v in fields.items():
            setattr(subscription, k, v)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def delete(self, subscription: Subscription):
        await self.session.delete(subscription)
        await self.session.commit()
