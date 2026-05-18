from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    guardian_id: int
    trigger_score: float
    channel: str
    sent_at: datetime

    class Config:
        from_attributes = True