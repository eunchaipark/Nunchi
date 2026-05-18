from pydantic import BaseModel
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    pin_token: str


class ChatResponse(BaseModel):
    id: int
    message: str        # AI 응답
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationHistory(BaseModel):
    id: int
    content: str        # 노인 발화
    fixed_content: str | None = None
    ai_response: str    # AI 응답
    created_at: datetime

    class Config:
        from_attributes = True