import strawberry
from strawberry import UNSET
from typing import Optional, List, Union
from strawberry.fastapi import GraphQLRouter
from datetime import date

from app.db.mongo_models import WeekPlan
from app.decorators.graphql_role_require import require_roles
from app.decorators.graphql_with_transaction import with_transaction

from app.services.client_service import ClientService
from app.services.membership_service import MembershipService
from app.services.subscription_service import SubscriptionService
from app.services.training_plan_service import TrainingPlanService
from app.schemas.postgres import ClientRead, ClientCreate, ClientUpdate, MembershipTypeUpdate, MembershipTypeCreate

from app.schemas.postgres import ClientCreate as PClientCreate
from app.schemas.postgres import SubscriptionCreate as PSubCreate
from app.schemas.postgres import VisitCreate as PVisitCreate
from app.services.visit_service import VisitService
from app.utils.graphql_to_dict import graphql_to_dict


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


@strawberry.type
class MembershipTypeType:
    id: int
    name: str
    duration_days: int
    price: float


@strawberry.input
class MembershipCreateInput:
    name: str
    duration_days: int
    price: float


@strawberry.input
class MembershipUpdateInput:
    name: Optional[str] = UNSET
    duration_days: Optional[int] = UNSET
    price: Optional[float] = UNSET


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

    # ---------- Membership ----------
    # ----------Get by ID Membership ----------
    @strawberry.field
    async def membership(self, info, membership_id: int) -> Optional[MembershipTypeType]:
        session = info.context["session"]
        svc = MembershipService(session)
        m = await svc.get(membership_id)
        if not m:
            return None
        return MembershipTypeType(
            id=m.id,
            name=m.name,
            duration_days=m.duration_days,
            price=float(m.price)
        )

    # ----------Get all Membership ----------
    @strawberry.field
    async def memberships(self, info, offset: int = 0, limit: int = 50) -> list[MembershipTypeType]:
        session = info.context["session"]
        svc = MembershipService(session)
        rows = await svc.list(offset, limit)
        return [
            MembershipTypeType(
                id=r.id,
                name=r.name,
                duration_days=r.duration_days,
                price=float(r.price)
            ) for r in rows
        ]


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
    @require_roles("ADMIN", "TRAINER")
    async def create_subscription(self, info, client_id: int, membership_type_id: int, start_date: date,
                                  end_date: date) -> bool:
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
    @require_roles("ADMIN", "TRAINER")
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

    # ---------- Membership ----------
    # ---------- CREATE ----------
    @strawberry.mutation
    @require_roles("ADMIN", "TRAINER")
    async def create_membership(
            self, info,
            data: MembershipCreateInput
    ) -> MembershipTypeType:

        session = info.context["session"]
        svc = MembershipService(session)

        created = await svc.create(
            MembershipTypeCreate(
                name=data.name,
                duration_days=data.duration_days,
                price=data.price
            )
        )

        return MembershipTypeType(
            id=created.id,
            name=created.name,
            duration_days=created.duration_days,
            price=float(created.price)
        )

    # ---------- UPDATE ----------
    @strawberry.mutation
    @require_roles("ADMIN", "TRAINER")
    async def update_membership(
            self, info,
            membership_id: int,
            data: MembershipUpdateInput
    ) -> Optional[MembershipTypeType]:

        session = info.context["session"]
        svc = MembershipService(session)

        update_payload = graphql_to_dict(data)

        updated = await svc.update(
            membership_id,
            MembershipTypeUpdate(**update_payload)
        )

        if not updated:
            return None

        return MembershipTypeType(
            id=updated.id,
            name=updated.name,
            duration_days=updated.duration_days,
            price=float(updated.price)
        )

    # ---------- DELETE ----------
    @strawberry.mutation
    @require_roles("ADMIN")  # delete только админам
    async def delete_membership(self, info, membership_id: int) -> bool:
        session = info.context["session"]
        svc = MembershipService(session)

        existing = await svc.get(membership_id)
        if not existing:
            return False

        await svc.repo.delete(existing)
        return True

    #TODO add create_training_plan

schema = strawberry.Schema(query=Query, mutation=Mutation)
