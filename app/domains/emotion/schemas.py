from pydantic import BaseModel
from datetime import datetime


class EmotionScoreResponse(BaseModel):
    id: int
    loneliness: float
    anxiety: float
    depression: float
    vitality: float
    connection: float
    hope: float
    overall_risk: float
    recorded_at: datetime

    class Config:
        from_attributes = True


class EmotionReportResponse(BaseModel):
    user_id: int
    avg_loneliness: float
    avg_anxiety: float
    avg_depression: float
    avg_vitality: float
    avg_connection: float
    avg_hope: float
    avg_overall_risk: float
    max_overall_risk: float
    period: str


class RiskResponse(BaseModel):
    user_id: int
    overall_risk: float
    status: str