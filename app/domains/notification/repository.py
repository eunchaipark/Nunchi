from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.models import GuardianAccess
from app.domains.notification.models import NotificationLog
from app.domains.user.models import User

class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_guardians_by_elder(self, elder_id:int) -> list[User]:
        result = await self.db.execute(
            select(User).join(
                GuardianAccess,GuardianAccess.guardian_id == User.id
            ).where(GuardianAccess.elder_id == elder_id)
        )
        return list(result.scalars().all())

    async def save_notification(
            self,
            user_id :int,
            guardian_id: int,
            trigger_score: float,
            channel : str = "email"
    ) -> NotificationLog :
        log = NotificationLog(
            user_id = user_id,
            guardian_id = guardian_id,
            trigger_score = trigger_score,
            channel = channel
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_notification_by_user(self, user_id:int) -> list[NotificationLog]:
        result = await self.db.execute(
            select(NotificationLog).where(NotificationLog.user_id == user_id)
            .order_by(NotificationLog.sent_at.desc())
        )
        return list(result.scalars().all())