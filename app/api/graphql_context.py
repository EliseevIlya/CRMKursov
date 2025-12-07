from fastapi import HTTPException, status, Depends, Request, Response

from app.core.security import get_current_user
from app.deps import get_session
from app.redis_client import redis_client_init

from sqlalchemy.ext.asyncio import AsyncSession


async def get_context(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> dict:
    """"
    Возвращает context, который потом попадёт в info.context в резолверах.
    request — starlette request.
    """
    current_user = None
    # Получаем текущего пользователя из заголовка Authorization (если есть)
    try:
        headers = request.headers
        auth = headers.get("authorization") or headers.get("Authorization")
        if not auth:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        token = parts[1]

        current_user = await get_current_user(token, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        # пробрасываем дальше (или ставим current_user = None)

    return {
        "request": request,
        "response": response,
        "session": session,
        "redis": redis_client_init,
        "user": current_user,
    }
