from fastapi import APIRouter, Depends
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.chat.repository import ChatRepository
from app.domains.chat.schemas import ChatRequest, ChatResponse, ConversationHistory
from app.domains.chat.service import ChatService
from app.domains.emotion.repository import EmotionRepository
from app.domains.user.models import User

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
        data: ChatRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = ChatRepository(db)
    emotion_repo = EmotionRepository(db)
    service = ChatService(repo, emotion_repo)
    return await service.chat(current_user, data)

@router.get("/history", response_model=list[ConversationHistory])
async def get_history(
        current_user: User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db)
):
    repo = ChatRepository(db)
    conversation =await repo.get_conversation(current_user.id)

    result = []
    for conv in conversation:
        result.append(ConversationHistory(
            id= conv.id,
            content=conv.encrypted_content,
            ai_response=conv.encrypted_ai_response,
            created_at=conv.created_at,
        ))
    return result
