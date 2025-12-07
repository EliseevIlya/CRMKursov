from functools import wraps
from app.deps import transactional
from sqlalchemy.ext.asyncio import AsyncSession


def with_transaction(func):
    """
    Декоратор для GraphQL-резолверов.
    Автоматически оборачивает переданную сессию в транзакцию.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Находим session в аргументах (обычно через info.context["session"])
        info = kwargs.get("info") or (args[1] if len(args) > 1 else None)
        if not info:
            raise ValueError("GraphQL info argument not found")

        session: AsyncSession = info.context.get("session")
        if not session:
            raise ValueError("Session not found in context")

        async with transactional(session):
            return await func(*args, **kwargs)

    return wrapper
