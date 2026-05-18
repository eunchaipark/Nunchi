from pydantic import BaseModel
from datetime import date


class UsageStatusResponse(BaseModel):
    user_id: int
    date: date
    voice_seconds: int
    text_count: int
    voice_limit_sec: int
    voice_remaining_sec: int
    text_limit: int
    text_remaining: int
    text_max_length: int
    plan: str


class QuotaCheckResponse(BaseModel):
    can_use: bool
    reason: str | None = None
    voice_remaining_sec: int
    text_remaining: int