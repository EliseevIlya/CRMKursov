from uuid import uuid4

from fastapi import APIRouter, Request, Depends
from authlib.integrations.starlette_client import OAuth

from app.config import settings
from app.db.models import User
from app.deps import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.postgres.user_repo import UserRepo
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = await oauth.google.parse_id_token(request, token)
    # userinfo contains 'email', 'sub', 'name', etc.
    email = userinfo.get("email")
    repo = UserRepo(session)
    user = await repo.get_by_email(email)
    auth_service = AuthService(session)

    if not user:
        # create user as CLIENT, random password (not used)
        hashed = auth_service.hash_password(uuid4().hex)
        new_user = User(email=email, password_hash=hashed, full_name=userinfo.get("name"), role="CLIENT",
                        is_active=True)
        user = await repo.create(user=new_user)
    # create jwt tokens and return them (or set cookie)
    tokens = await auth_service.create_tokens(user=user)
    # Option: redirect to frontend with tokens as query params or set httpOnly cookie
    return {"user": {"id": user.id, "email": user.email}, **tokens}
