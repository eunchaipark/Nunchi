from fastapi import APIRouter, Depends
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.notification.repository import NotificationRepository
from app.domains.notification.schemas import NotificationResponse
from app.domains.notification.service import NotificationService
from app.domains.user.models import User

router = APIRouter(prefix="/notification", tags=["notification"])


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = NotificationRepository(db)
    return await repo.get_notifications_by_user(current_user.id)