from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4
from jose import jwt, JWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.deps import get_session
from app.repositories.postgres.user_repo import UserRepo

from app.config import settings


def create_access_token(
        subject: int,
        role: str,
        expires_minutes: Optional[int] = None,
        issuer: Optional[str] = None
) -> str:
    """
    Создаёт access token с дополнительными проверками безопасности.
    """
    now = datetime.utcnow()
    expire = now + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": now,  # время выдачи
        "nbf": now,  # действителен с этого момента
        "iss": issuer or settings.ISSUER  # эмитенту
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(
        subject: int,
        jti: Optional[str] = None,
        expires_days: Optional[int] = None,
        issuer: Optional[str] = None
) -> tuple[str, str]:
    """
    Создаёт refresh token с уникальным ID.
    """
    jti = jti or str(uuid4())
    now = datetime.utcnow()
    expire = now + timedelta(
        days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(subject),
        "jti": jti,
        "exp": expire,
        "iat": now,
        "nbf": now,
        "iss": issuer or settings.ISSUER
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti


def decode_token(token: str, expected_issuer: Optional[str] = None) -> Dict[str, Any]:
    """
    Декодирует токен с полной валидацией.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "require_exp": True,
                "require_iat": True,
                "require_nbf": True
            }
        )

        # Проверка эмитента, если указан
        if expected_issuer and payload.get("iss") != expected_issuer:
            raise jwt.InvalidIssuerError("Invalid issuer")

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid token issuer")
    except jwt.ImmatureSignatureError:
        raise ValueError("Token not yet valid")
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(get_session)):
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repo = UserRepo(session)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def role_required(*roles: str):
    async def role_checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return role_checker
