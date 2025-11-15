from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Numeric, BigInteger, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)


class Client(Base):
    __tablename__ = "clients"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    full_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)


class MembershipType(Base):
    __tablename__ = "membership_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Numeric(10,2), nullable=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True)
    client_id = Column(BigInteger, ForeignKey("clients.id"))
    membership_type_id = Column(Integer, ForeignKey("membership_types.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)


class Visit(Base):
    __tablename__ = "visits"

    id = Column(BigInteger, primary_key=True)
    client_id = Column(BigInteger, ForeignKey("clients.id"))
    trainer_id = Column(Integer, ForeignKey("users.id"))
    visit_time = Column(TIMESTAMP)
