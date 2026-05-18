from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from app.domains.emotion.models import EmotionLog


class EmotionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_emotion(self, user_id: int, conversation_id: int, scores: dict) -> EmotionLog:
        emotion = EmotionLog(
            user_id=user_id,
            conversation_id=conversation_id,
            loneliness=scores.get("loneliness", 0),
            anxiety=scores.get("anxiety", 0),
            depression=scores.get("depression", 0),
            vitality=scores.get("vitality", 0),
            connection=scores.get("connection", 0),
            hope=scores.get("hope", 0),
            overall_risk=self._calc_overall_risk(scores),
        )
        self.db.add(emotion)
        await self.db.flush()
        return emotion

    async def get_scores_by_user(self, user_id: int) -> list[EmotionLog]:
        result = await self.db.execute(
            select(EmotionLog)
            .where(EmotionLog.user_id == user_id)
            .order_by(EmotionLog.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def get_daily_average(self, user_id: int, target_date: date) -> dict | None:
        result = await self.db.execute(
            select(
                func.avg(EmotionLog.loneliness).label("avg_loneliness"),
                func.avg(EmotionLog.anxiety).label("avg_anxiety"),
                func.avg(EmotionLog.depression).label("avg_depression"),
                func.avg(EmotionLog.vitality).label("avg_vitality"),
                func.avg(EmotionLog.connection).label("avg_connection"),
                func.avg(EmotionLog.hope).label("avg_hope"),
                func.avg(EmotionLog.overall_risk).label("avg_overall_risk"),
                func.max(EmotionLog.overall_risk).label("max_overall_risk"),
            )
            .where(EmotionLog.user_id == user_id)
            .where(func.date(EmotionLog.recorded_at) == target_date)
        )
        row = result.fetchone()
        if not row or row.avg_overall_risk is None:
            return None
        return {
            "avg_loneliness": round(row.avg_loneliness, 2),
            "avg_anxiety": round(row.avg_anxiety, 2),
            "avg_depression": round(row.avg_depression, 2),
            "avg_vitality": round(row.avg_vitality, 2),
            "avg_connection": round(row.avg_connection, 2),
            "avg_hope": round(row.avg_hope, 2),
            "avg_overall_risk": round(row.avg_overall_risk, 2),
            "max_overall_risk": round(row.max_overall_risk, 2),
        }

    @staticmethod
    def _calc_overall_risk(scores: dict) -> float:
        negative = (scores.get("loneliness", 0) + scores.get("anxiety", 0) + scores.get("depression", 0)) / 3
        positive = (scores.get("vitality", 0) + scores.get("connection", 0) + scores.get("hope", 0)) / 3
        return round((negative * 0.7) + ((10 - positive) * 0.3), 2)