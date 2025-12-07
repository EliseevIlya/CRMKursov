import strawberry
from typing import Optional, List
from strawberry.fastapi import GraphQLRouter
from datetime import date

from app.db.mongo_models import WeekPlan
from app.decorators.graphql_role_require import require_roles
# импорт твоих сервисов и pydantic-схем/моделей
from app.services.client_service import ClientService
from app.services.subscription_service import SubscriptionService
from app.services.training_plan_service import TrainingPlanService
from app.schemas.postgres import ClientRead, ClientCreate, ClientUpdate

from app.schemas.postgres import ClientCreate as PClientCreate
from app.schemas.postgres import SubscriptionCreate as PSubCreate
from app.schemas.postgres import VisitCreate as PVisitCreate
from app.services.visit_service import VisitService


# --- GraphQL types (маленькая обёртка для ответа) ---
@strawberry.type
class ClientType:
    id: strawberry.ID
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    is_active: bool
    has_active_subscription: bool


@strawberry.type
class ExerciseType:
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    notes: Optional[str] = None


@strawberry.type
class DayPlanType:
    day: str
    exercises: List[ExerciseType]


@strawberry.type
class WeekPlanType:
    week: int
    days: List[DayPlanType]


@strawberry.type
class TrainingPlanType:
    id: strawberry.ID
    trainer_id: int
    weeks: List[WeekPlanType]
    notes: str


# Можно использовать pydantic -> strawberry conversion, но ручной контролируемый тип проще

# --- Query ---
@strawberry.type
class Query:
    @strawberry.field
    async def test(self, info) -> str:
        return "GraphQL работает!"

    @strawberry.field
    async def client(self, info, client_id: int) -> Optional[ClientType]:
        session = info.context["session"]
        svc = ClientService(session)
        payload = await svc.get(client_id)
        if not payload:
            return None
        return ClientType(
            id=str(payload["id"]),
            email=payload["email"],
            full_name=payload.get("full_name"),
            phone=payload.get("phone"),
            is_active=payload.get("is_active", True),
            has_active_subscription=payload.get("has_active_subscription", False)
        )

    @strawberry.field
    async def clients(self, info, offset: int = 0, limit: int = 50) -> List[ClientType]:
        session = info.context["session"]
        svc = ClientService(session)
        rows = await svc.list(offset, limit)
        result = []
        for r in rows:
            # r — SQLAlchemy Client instance
            # можно получить has_active через svc.subs.get_active_by_client(r.id)
            active_sub = await svc.subs.get_active_by_client(r.id)
            result.append(ClientType(
                id=str(r.id), email=r.email, full_name=r.full_name, phone=r.phone,
                is_active=r.is_active, has_active_subscription=bool(active_sub)
            ))
        return result

    @strawberry.field
    async def training_plans(self, info, client_id: int) -> List[TrainingPlanType]:
        session = info.context["session"]
        svc = TrainingPlanService()
        plans = await svc.list_for_client(client_id)
        # преобразуй планы в типы GraphQL
        return [TrainingPlanType(...) for p in plans]


# --- Mutations ---
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_client(self, info, email: str, password: Optional[str] = None, full_name: Optional[str] = None,
                            phone: Optional[str] = None) -> ClientType:
        session = info.context["session"]
        svc = ClientService(session)
        # формируем pydantic-объект или словарь
        payload = PClientCreate(email=email, password=password, full_name=full_name, phone=phone)
        created = await svc.create(payload)
        return ClientType(id=str(created.id), email=created.email, full_name=created.full_name, phone=created.phone,
                          is_active=created.is_active, has_active_subscription=False)

    @strawberry.mutation
    @require_roles("ADMIN", "TRAINER", "USER")
    async def create_subscription(self, info, client_id: int, membership_type_id: int, start_date: date,
                                  end_date: date) -> bool:
        # Проверяем авторизацию: только авторизованные пользователи (например, админ/кассир) могут
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        session = info.context["session"]
        svc = SubscriptionService(session)
        p = PSubCreate(client_id=client_id, membership_type_id=membership_type_id, start_date=start_date,
                       end_date=end_date, is_active=True)
        await svc.create(p)
        return True

    @strawberry.mutation
    @require_roles("ADMIN", "TRAINER", "USER")
    async def create_visit(self, info, client_id: int, trainer_id: Optional[int] = None,
                           visit_time: Optional[str] = None) -> bool:
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        session = info.context["session"]
        payload = PVisitCreate(client_id=client_id, trainer_id=trainer_id, visit_time=visit_time)
        svc = VisitService(session)
        await svc.create(payload)
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
#graphql_app = GraphQLRouter(schema, path="/graphql",context_getter=lambda request: request.app.state.get("graphql_context"))
