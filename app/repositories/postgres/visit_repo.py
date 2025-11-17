from sqlalchemy import select
from typing import List, Optional
from app.db.models import Visit
from app.repositories.postgres.base import BaseRepo


class VisitRepo(BaseRepo):
    async def get(self, visit_id: int) -> Optional[Visit]:
        q = await self.session.execute(select(Visit).where(Visit.id == visit_id))
        return q.scalars().first()

    async def list(self, offset: int = 0, limit: int = 50) -> List[Visit]:
        q = await self.session.execute(select(Visit).offset(offset).limit(limit))
        return q.scalars().all()

    async def create(self, visit: Visit) -> Visit:
        self.session.add(visit)
        await self.session.commit()
        await self.session.refresh(visit)
        return visit
