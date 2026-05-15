from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base import Base


class GuardianAccess(Base):
    __tablename__ = "guardian_access"

    guardian_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    elder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    can_view_score: Mapped[bool] = mapped_column(Boolean, default=True)
    can_view_content: Mapped[bool] = mapped_column(Boolean, default=False)
    granted_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())