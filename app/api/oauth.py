from http.client import HTTPException
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
    #client_kwargs={"scope": "openid email profile", "state": True},
)


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    print("DEBUG redirect_uri =", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    try:
        #userinfo = await oauth.google.parse_id_token(request, token)
        resp = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
        userinfo = resp.json()
    except Exception:
        raise HTTPException(400, "Invalid Google token")
    # userinfo contains 'email', 'sub', 'name', etc.
    email = userinfo.get("email")
    if not email:
        raise HTTPException(400, "Google account does not provide email")
    repo = UserRepo(session)
    user = await repo.get_by_email(email)
    auth_service = AuthService(session)

    if not user:
        # create user as ADMIN, random password (not used)
        #TODO add  auth_provider instead ( google / self)
        hashed = auth_service.hash_password(uuid4().hex)
        new_user = User(email=email, password_hash=hashed, full_name=userinfo.get("name"), role="CLIENT",
                        is_active=True)
        user = await repo.create(user=new_user)
    # create jwt tokens and return them (or set cookie)
    tokens = await auth_service.create_tokens(user=user)
    # Option: redirect to frontend with tokens as query params or set httpOnly cookie
    return {"user": {"id": user.id, "email": user.email}, **tokens}
