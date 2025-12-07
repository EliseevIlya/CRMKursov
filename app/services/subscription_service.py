from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.postgres.membership_repo import MembershipRepo
from app.repositories.postgres.subscription_repo import SubscriptionRepo
from app.repositories.postgres.client_repo import ClientRepo
from app.db.models import Subscription
from app.repositories.redis.active_client_cache import ActiveClientCache
from app.schemas.postgres import SubscriptionCreate, SubscriptionUpdate
from app.services.payment_service import PaymentService

""""
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
"""


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.repo = SubscriptionRepo(session)
        self.clients = ClientRepo(session)
        self.memberships = MembershipRepo(session)
        self.payment = PaymentService()  # внутренний сервис, абстракт

    async def get(self, subscription_id: int):
        return await self.repo.get(subscription_id)

    async def get_active_for_client(self, client_id: int):
        return await self.repo.get_active_by_client(client_id)

    async def create(self, data: SubscriptionCreate):
        client = await self.clients.get(data.client_id)
        if not client:
            raise ValueError("Client not found")

        membership = await self.memberships.get(data.membership_type_id)
        if not membership:
            raise ValueError("Membership not found")

        # Пример транзакции: charge + создать subscription
        async with self.session.begin():  # откроет транзакцию
            # 1) charge через payment gateway (может бросить исключение)
            payment_res = await self.payment.charge(client_id=data.client_id, amount=float(membership.price))
            if not payment_res.get("ok"):
                raise ValueError("Payment failed")

            # 2) создать subscription
            sub = Subscription(
                client_id=data.client_id,
                membership_type_id=data.membership_type_id,
                start_date=data.start_date,
                end_date=data.end_date,
                is_active=True
            )
            self.session.add(sub)
            # session.begin() автоматически коммитит при выходе, или откатит при исключении
        # invalidate cache

        await ActiveClientCache().delete(data.client_id)
        return sub

    async def renew(self, subscription_id: int, renew_data: SubscriptionUpdate = None):
        sub = await self.repo.get(subscription_id)
        if not sub:
            raise ValueError("Subscription not found")

        membership = await self.memberships.get(sub.membership_type_id)
        if not membership:
            raise ValueError("Membership type not found")

        new_end = sub.end_date + timedelta(days=membership.duration_days)
        async with self.session.begin():
            payment_res = await self.payment.charge(client_id=sub.client_id, amount=float(membership.price))
            if not payment_res.get("ok"):
                raise ValueError("Payment failed")
            sub.end_date = new_end
            sub.is_active = True
            self.session.add(sub)

        # invalidate cache
        await ActiveClientCache().delete(sub.client_id)
        return sub