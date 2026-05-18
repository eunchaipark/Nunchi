from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.chat.repository import ChatRepository
from app.domains.chat.schemas import ChatRequest, ChatResponse, ConversationHistory
from app.domains.chat.service import ChatService
from app.domains.emotion.repository import EmotionRepository
from app.domains.notification.repository import NotificationRepository
from app.domains.usage.repository import UsageRepository
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
    notification_repo = NotificationRepository(db)
    usage_repo = UsageRepository(db)
    service = ChatService(repo, emotion_repo, notification_repo, usage_repo)
    return await service.chat(current_user, data)

@router.get("/history", response_model=list[ConversationHistory])
async def get_history(
        pin_token: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    from app.core.security import decode_pin_token, decrypt
    try:
        pin = decode_pin_token(pin_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    repo = ChatRepository(db)
    conversation = await repo.get_conversation(current_user.id)

    result = []
    for conv in conversation:
        try:
            content = decrypt(conv.encrypted_content, pin)
            ai_response = decrypt(conv.encrypted_ai_response, pin)
            fixed_content = decrypt(conv.encrypted_fixed_content, pin) if conv.encrypted_fixed_content else None
        except Exception:
            continue
        result.append(ConversationHistory(
            id=conv.id,
            content=content,
            fixed_content=fixed_content,
            ai_response=ai_response,
            created_at=conv.created_at,
        ))
    return result
