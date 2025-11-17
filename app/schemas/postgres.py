from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ---------- User ----------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "CLIENT"
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Client ----------
class ClientBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True


class ClientCreate(ClientBase):
    password: Optional[str] = None


class ClientUpdate(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]
    is_active: Optional[bool]


class ClientRead(ClientBase):
    id: int

    class Config:
        from_attributes = True


# ---------- MembershipType ----------
class MembershipTypeBase(BaseModel):
    name: str
    duration_days: int
    price: float


class MembershipTypeCreate(MembershipTypeBase): ...


class MembershipTypeUpdate(BaseModel):
    name: Optional[str]
    duration_days: Optional[int]
    price: Optional[float]


class MembershipTypeRead(MembershipTypeBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Subscription ----------
class SubscriptionBase(BaseModel):
    client_id: int
    membership_type_id: int
    start_date: date
    end_date: date
    is_active: Optional[bool] = True


class SubscriptionCreate(SubscriptionBase): ...


class SubscriptionUpdate(BaseModel):
    end_date: Optional[date]
    is_active: Optional[bool]


class SubscriptionRead(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Visit ----------
class VisitBase(BaseModel):
    client_id: int
    trainer_id: Optional[int]
    visit_time: Optional[datetime]


class VisitCreate(VisitBase): ...


class VisitUpdate(BaseModel):
    visit_time: Optional[datetime]


class VisitRead(VisitBase):
    id: int

    class Config:
        from_attributes = True
