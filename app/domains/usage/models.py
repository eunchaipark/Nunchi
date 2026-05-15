from sqlalchemy import Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    voice_seconds: Mapped[int] = mapped_column(Integer, default=0)
    text_count: Mapped[int] = mapped_column(Integer, default=0)