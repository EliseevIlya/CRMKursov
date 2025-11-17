from fastapi import APIRouter, Depends, HTTPException, status

from app.db.models import User
from app.schemas.postgres import UserCreate  # reuse or create Auth schemas
from app.services.auth_service import AuthService
from app.deps import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    auth = AuthService(session)
    existing = await auth.user_repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.hash_password(payload.password)
    new_user = User(email=payload.email, password_hash=hashed, full_name=payload.full_name, role=payload.role,
                    is_active=True)

    user = await auth.user_repo.create(user=new_user)
    tokens = await auth.create_tokens(user)
    return {"user": {"id": user.id, "email": user.email}, **tokens}


@router.post("/login")
async def login(form_data: dict, session: AsyncSession = Depends(get_session)):
    # if you prefer OAuth2PasswordRequestForm:
    # from fastapi.security import OAuth2PasswordRequestForm
    # form_data: OAuth2PasswordRequestForm = Depends()
    # email = form_data.username; password = form_data.password
    email = form_data.get("email")
    password = form_data.get("password")
    auth = AuthService(session)
    user = await auth.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = await auth.create_tokens(user)
    return tokens


@router.post("/refresh")
async def refresh(payload: dict, session: AsyncSession = Depends(get_session)):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400)
    auth = AuthService(session)  # note: user_repo uses session; if not needed, adapt
    data = await auth.refresh_access_token(refresh_token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return data


@router.post("/logout")
async def logout(payload: dict, session: AsyncSession = Depends(get_session)):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400)
    auth = AuthService(session)
    await auth.revoke_refresh(refresh_token)
    return {"ok": True}
