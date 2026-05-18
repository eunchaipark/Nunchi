from datetime import date
from fastapi import HTTPException
from app.domains.emotion.repository import EmotionRepository
from app.domains.emotion.schemas import EmotionReportResponse, RiskResponse


class EmotionService:
    def __init__(self, repo: EmotionRepository):
        self.repo = repo

    async def get_daily(self, user_id: int, target_date: date) -> EmotionReportResponse:
        result = await self.repo.get_daily_average(user_id, target_date)
        if not result:
            raise HTTPException(status_code=404, detail="해당 날짜의 감정 데이터가 없어요")
        return EmotionReportResponse(
            user_id=user_id,
            avg_loneliness=result["avg_loneliness"],
            avg_anxiety=result["avg_anxiety"],
            avg_depression=result["avg_depression"],
            avg_vitality=result["avg_vitality"],
            avg_connection=result["avg_connection"],
            avg_hope=result["avg_hope"],
            avg_overall_risk=result["avg_overall_risk"],
            max_overall_risk=result["max_overall_risk"],
            period=str(target_date),
        )

    async def get_risk(self, user_id: int) -> RiskResponse:
        result = await self.repo.get_daily_average(user_id, date.today())
        if not result:
            return RiskResponse(
                user_id=user_id,
                overall_risk=0.0,
                status="데이터 없음"
            )

        risk = result["avg_overall_risk"]
        if risk >= 7.0:
            status = "위험"
        elif risk >= 5.0:
            status = "주의"
        else:
            status = "안정"

        return RiskResponse(
            user_id=user_id,
            overall_risk=risk,
            status=status
        )