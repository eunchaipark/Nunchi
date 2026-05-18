from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domains.usage.models import UsageLog
from app.domains.user.models import UserPlan


class UsageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_today(self, user_id: int) -> UsageLog:
        today = date.today()
        result = await self.db.execute(
            select(UsageLog)
            .where(UsageLog.user_id == user_id)
            .where(UsageLog.date == today)
        )
        usage = result.scalar_one_or_none()
        if not usage:
            usage = UsageLog(
                user_id=user_id,
                date=today,
                voice_seconds=0,
                text_count=0,
            )
            self.db.add(usage)
            await self.db.flush()
        return usage

    async def get_plan(self, user_id: int) -> UserPlan | None:
        result = await self.db.execute(
            select(UserPlan).where(UserPlan.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def add_voice_seconds(self, user_id: int, seconds: int) -> UsageLog:
        usage = await self.get_or_create_today(user_id)
        usage.voice_seconds += seconds
        await self.db.flush()
        return usage

    async def add_text_count(self, user_id: int) -> UsageLog:
        usage = await self.get_or_create_today(user_id)
        usage.text_count += 1
        await self.db.flush()
        return usage