from sqlalchemy import select
from typing import List, Optional
from app.db.models import MembershipType
from app.repositories.postgres.base import BaseRepo


class MembershipRepo(BaseRepo):
    async def get(self, membership_id: int) -> Optional[MembershipType]:
        q = await self.session.execute(select(MembershipType).where(MembershipType.id == membership_id))
        return q.scalars().first()

    async def list(self, offset: int = 0, limit: int = 50) -> List[MembershipType]:
        q = await self.session.execute(select(MembershipType).offset(offset).limit(limit))
        return q.scalars().all()

    async def create(self, membership: MembershipType) -> MembershipType:
        self.session.add(membership)
        await self.session.commit()
        await self.session.refresh(membership)
        return membership

    async def update(self, membership: MembershipType, **fields) -> MembershipType:
        for k, v in fields.items():
            setattr(membership, k, v)
        await self.session.commit()
        await self.session.refresh(membership)
        return membership

    async def delete(self, membership: MembershipType):
        await self.session.delete(membership)
        await self.session.commit()
