from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories.postgres.user_repo import UserRepo
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.services.refresh_token_service import RefreshTokenStore
from datetime import datetime

pwd_ctx = CryptContext(schemes=[settings.CRYPT_SCHEME], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepo(session)

    # password helpers
    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_ctx.verify(plain, hashed)

    def hash_password(self, plain: str) -> str:
        return pwd_ctx.hash(plain)

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user: return None
        if not self.verify_password(password, user.password_hash): return None
        if not user.is_active: return None
        return user

    async def create_tokens(self, user):
        access = create_access_token(subject=user.id, role=user.role)
        refresh, jti = create_refresh_token(subject=user.id)
        await RefreshTokenStore.save(user.id, jti, refresh)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
            user_id = int(payload.get("sub"))
            jti = payload.get("jti")
        except Exception:
            return None
        # check in redis
        ok = await RefreshTokenStore.exists(user_id, jti)
        if not ok:
            return None
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        # create new access & optionally rotate refresh
        access = create_access_token(subject=user.id, role=user.role)
        # Optionally implement refresh rotation: create new refresh, save & delete old
        return {"access_token": access, "token_type": "bearer"}

    async def revoke_refresh(self, refresh_token: str):
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
        jti = payload.get("jti")
        await RefreshTokenStore.delete(user_id, jti)
