from fastapi import HTTPException
from app.domains.usage.repository import UsageRepository
from app.domains.usage.schemas import UsageStatusResponse, QuotaCheckResponse


class UsageService:
    def __init__(self, repo: UsageRepository):
        self.repo = repo

    async def check_quota(self, user_id: int, voice_seconds: int = 0) -> QuotaCheckResponse:
        usage = await self.repo.get_or_create_today(user_id)
        plan = await self.repo.get_plan(user_id)

        if not plan:
            raise HTTPException(status_code=404, detail="플랜 정보가 없어요")

        # 음성 체크
        if voice_seconds > 0:
            remaining_voice = plan.voice_limit_sec - usage.voice_seconds
            if remaining_voice < 5:
                return QuotaCheckResponse(
                    can_use=False,
                    reason="오늘 음성 한도를 다 사용했어요",
                    voice_remaining_sec=0,
                    text_remaining=max(0, plan.text_limit - usage.text_count),
                )
            if voice_seconds > remaining_voice:
                return QuotaCheckResponse(
                    can_use=False,
                    reason=f"음성 시간이 부족해요. 남은 시간: {remaining_voice}초",
                    voice_remaining_sec=remaining_voice,
                    text_remaining=max(0, plan.text_limit - usage.text_count),
                )

        # 텍스트 체크 (무제한은 -1)
        if plan.text_limit != -1:
            if usage.text_count >= plan.text_limit:
                return QuotaCheckResponse(
                    can_use=False,
                    reason="오늘 텍스트 한도를 다 사용했어요",
                    voice_remaining_sec=max(0, plan.voice_limit_sec - usage.voice_seconds),
                    text_remaining=0,
                )

        voice_remaining = plan.voice_limit_sec - usage.voice_seconds if plan.voice_limit_sec != -1 else -1
        text_remaining = plan.text_limit - usage.text_count if plan.text_limit != -1 else -1

        return QuotaCheckResponse(
            can_use=True,
            voice_remaining_sec=voice_remaining,
            text_remaining=text_remaining,
        )

    async def consume(self, user_id: int, voice_seconds: int = 0) -> None:
        if voice_seconds > 0:
            await self.repo.add_voice_seconds(user_id, voice_seconds)
        else:
            await self.repo.add_text_count(user_id)

    async def get_status(self, user_id: int) -> UsageStatusResponse:
        usage = await self.repo.get_or_create_today(user_id)
        plan = await self.repo.get_plan(user_id)

        if not plan:
            raise HTTPException(status_code=404, detail="플랜 정보가 없어요")

        voice_remaining = max(0, plan.voice_limit_sec - usage.voice_seconds)
        text_remaining = max(0, plan.text_limit - usage.text_count)

        return UsageStatusResponse(
            user_id=user_id,
            date=usage.date,
            voice_seconds=usage.voice_seconds,
            text_count=usage.text_count,
            voice_limit_sec=plan.voice_limit_sec,
            voice_remaining_sec=voice_remaining,
            text_limit=plan.text_limit,
            text_remaining=text_remaining,
            text_max_length=plan.text_max_length,
            plan=plan.plan,
        )