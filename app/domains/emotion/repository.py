from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.emotion.models import EmotionLog


class EmotionRepository:
    def __init__(self, db : AsyncSession):
        self.db = db

    async def save_emotion(
            self,
            user_id: int,
            conversation_id : int,
            scores : dict,
    ) -> EmotionLog:
        emotion = EmotionLog(
            user_id = user_id,
            conversation_id = conversation_id,
            loneliness=scores.get('loneliness',0),
            anxiety=scores.get('anxiety',0),
            depression=scores.get('depression',0),
            vitality=scores.get('vitality',0),
            connection=scores.get('connection',0),
            hope=scores.get('hope',0),
            overall_risk=self._calc_overall_risk(scores),
        )
        self.db.add(emotion)
        await self.db.flush()
        return emotion

    @staticmethod
    def _calc_overall_risk(scores : dict) -> float:
        loneliness = scores.get('loneliness',0)
        anxiety = scores.get('anxiety',0)
        depression = scores.get('depression',0)
        vitality = scores.get('vitality',0)
        connection = scores.get('connection',0)
        hope = scores.get('hope',0)
        negative = (loneliness + anxiety + depression) / 3
        positive = (loneliness + anxiety + depression) / 3
        return round((negative * 0.7 ) + (10 -positive) * 0.3, 2)