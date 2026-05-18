from fastapi import APIRouter, Depends
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.usage.repository import UsageRepository
from app.domains.usage.schemas import UsageStatusResponse
from app.domains.usage.service import UsageService
from app.domains.user.models import User

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/", response_model=UsageStatusResponse)
async def get_usage(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = UsageRepository(db)
    service = UsageService(repo)
    return await service.get_status(current_user.id)