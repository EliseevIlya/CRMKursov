from sqlalchemy import select
from typing import List, Optional
from app.db.models import Client
from app.repositories.postgres.base import BaseRepo

class ClientRepo(BaseRepo):
    async def get(self, client_id: int) -> Optional[Client]:
        q = await self.session.execute(select(Client).where(Client.id == client_id))
        return q.scalars().first()

    async def list(self, offset: int = 0, limit: int = 50) -> List[Client]:
        q = await self.session.execute(select(Client).offset(offset).limit(limit))
        return q.scalars().all()

    async def create(self, client: Client) -> Client:
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def update(self, client: Client, **fields) -> Client:
        for k, v in fields.items():
            setattr(client, k, v)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def delete(self, client: Client):
        await self.session.delete(client)
        await self.session.commit()
