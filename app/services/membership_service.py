from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.postgres.membership_repo import MembershipRepo
from app.db.models import MembershipType
from app.schemas.postgres import MembershipTypeCreate, MembershipTypeUpdate


class MembershipService:
    def __init__(self, session: AsyncSession):
        self.repo = MembershipRepo(session)

    async def get(self, membership_id: int):
        return await self.repo.get(membership_id)

    async def list(self, offset: int = 0, limit: int = 50):
        return await self.repo.list(offset, limit)

    async def create(self, data: MembershipTypeCreate):
        m = MembershipType(name=data.name, duration_days=data.duration_days, price=data.price)
        return await self.repo.create(m)

    async def update(self, membership_id: int, data: MembershipTypeUpdate):
        m = await self.repo.get(membership_id)
        if not m: return None
        return await self.repo.update(m, **data.dict(exclude_unset=True))
