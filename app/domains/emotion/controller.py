from datetime import date
from fastapi import APIRouter, Depends
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.emotion.repository import EmotionRepository
from app.domains.emotion.schemas import EmotionReportResponse, RiskResponse
from app.domains.emotion.service import EmotionService
from app.domains.user.models import User

router = APIRouter(prefix="/emotion", tags=["emotion"])


@router.get("/{user_id}/daily", response_model=EmotionReportResponse)
async def get_daily(
        user_id: int,
        target_date: date,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = EmotionRepository(db)
    service = EmotionService(repo)
    return await service.get_daily(user_id, target_date)


@router.get("/{user_id}/risk", response_model=RiskResponse)
async def get_risk(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = EmotionRepository(db)
    service = EmotionService(repo)
    return await service.get_risk(user_id)