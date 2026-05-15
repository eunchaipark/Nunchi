from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    guardian_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    trigger_score: Mapped[float] = mapped_column(Float, nullable=False)
    sent_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    channel: Mapped[str] = mapped_column(String(10), nullable=False)