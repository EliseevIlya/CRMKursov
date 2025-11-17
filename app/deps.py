from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.user_service import UserService
from app.services.client_service import ClientService
from app.services.membership_service import MembershipService
from app.services.subscription_service import SubscriptionService
from app.services.visit_service import VisitService
from app.services.training_plan_service import TrainingPlanService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# service providers
async def get_user_service(session: AsyncSession = Depends(get_session)):
    return UserService(session)


async def get_client_service(session: AsyncSession = Depends(get_session)):
    return ClientService(session)


async def get_membership_service(session: AsyncSession = Depends(get_session)):
    return MembershipService(session)


async def get_subscription_service(session: AsyncSession = Depends(get_session)):
    return SubscriptionService(session)


async def get_visit_service(session: AsyncSession = Depends(get_session)):
    return VisitService(session)


async def get_training_plan_service():
    return TrainingPlanService()
