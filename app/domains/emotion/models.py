from sqlalchemy import Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base import Base


class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), nullable=False)
    loneliness: Mapped[float] = mapped_column(Float, nullable=False)
    anxiety: Mapped[float] = mapped_column(Float, nullable=False)
    depression: Mapped[float] = mapped_column(Float, nullable=False)
    vitality: Mapped[float] = mapped_column(Float, nullable=False)
    connection: Mapped[float] = mapped_column(Float, nullable=False)
    hope: Mapped[float] = mapped_column(Float, nullable=False)
    overall_risk: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())