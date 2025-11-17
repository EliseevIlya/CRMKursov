from sqlalchemy import select
from app.db.models import User
from typing import List, Optional
from app.repositories.postgres.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_by_id(self, user_id: int) -> Optional[User]:
        q = await self.session.execute(select(User).where(User.id == user_id))
        return q.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        q = await self.session.execute(select(User).where(User.email == email))
        return q.scalars().first()

    async def list(self, offset: int = 0, limit: int = 50) -> List[User]:
        q = await self.session.execute(select(User).offset(offset).limit(limit))
        return q.scalars().all()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, **fields) -> User:
        for k, v in fields.items():
            setattr(user, k, v)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User):
        await self.session.delete(user)
        await self.session.commit()
