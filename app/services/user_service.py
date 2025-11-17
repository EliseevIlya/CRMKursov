from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories.postgres.user_repo import UserRepo
from app.schemas.postgres import UserCreate, UserUpdate, UserRead
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=[settings.CRYPT_SCHEME], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepo(session)

    async def get(self, user_id: int) -> User | None:
        return await self.repo.get_by_id(user_id)

    async def list(self, offset: int = 0, limit: int = 50):
        return await self.repo.list(offset, limit)

    async def create(self, data: UserCreate) -> User:
        hashed = pwd_context.hash(data.password)
        user = User(email=data.email, password_hash=hashed, full_name=data.full_name, role=data.role,
                    is_active=data.is_active)
        return await self.repo.create(user)

    async def update(self, user_id: int, data: UserUpdate):
        user = await self.repo.get_by_id(user_id)
        if not user:
            return None
        return await self.repo.update(user, **data.dict(exclude_unset=True))
