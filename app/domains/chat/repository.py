from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.repository import AuthRepository
from app.domains.chat.models import Conversation


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_conversation(
            self,
            user_id: int,
            content: str,
            fixed_content: str | None,
            ai_response: str,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            encrypted_content=content,
            encrypted_fixed_content=fixed_content,
            encrypted_ai_response=ai_response,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def get_recent_conversations(
            self, user_id: int, limit: int = 5
    ) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        conversations = result.scalars().all()
        return list(reversed(conversations))


    async def get_conversation(
            self, user_id: int
    ) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())