import functools
import strawberry
from typing import Callable, TypeVar, Any

T = TypeVar("T", bound=Callable[..., Any])


def require_roles(*allowed_roles: str) -> Callable[[T], T]:
    """
    Декоратор для проверки ролей пользователя в Strawberry GraphQL резолверах.
    Можно использовать на @strawberry.field и @strawberry.mutation.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(self, info: strawberry.types.Info, *args, **kwargs):
            user = info.context.get("user")
            if not user:
                raise Exception("Authentication required")
            if user.role not in allowed_roles:
                raise Exception("Forbidden")
            return await func(self, info, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator
