from sqlalchemy import Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    encrypted_content: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_fixed_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    encrypted_ai_response: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())