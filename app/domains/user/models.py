from sqlalchemy import String, Boolean, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.core.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kakao_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    has_pin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())


class UserPlan(Base):
    __tablename__ = "user_plans"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan: Mapped[str] = mapped_column(String(10), nullable=False)
    voice_limit_sec: Mapped[int] = mapped_column(Integer, nullable=False)