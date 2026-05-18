from app.core.ai_client import AIClient
from app.domains.chat.repository import ChatRepository
from app.domains.chat.schemas import ChatRequest, ChatResponse
from app.domains.emotion.repository import EmotionRepository
from app.domains.user.models import User

SYSTEM_PROMPT = """
당신은 독거노인의 말벗이 되어주는 따뜻한 AI입니다.
노인분들의 말씀을 경청하고 공감하며 대화를 이어나가세요.
방언이나 오타가 있어도 문맥으로 이해하고 자연스럽게 대화하세요.
짧고 친근하게 답변하세요.

대화 마지막에 반드시 아래 JSON을 붙여주세요:
[EMOTION_SCORE]
{"loneliness": 0~10, "anxiety": 0~10, "depression": 0~10, "vitality": 0~10, "connection": 0~10, "hope": 0~10}
[/EMOTION_SCORE]
"""


class ChatService:
    def __init__(self, repo: ChatRepository, emotion_repo: EmotionRepository):
        self.repo = repo
        self.emotion_repo = emotion_repo

    async def chat(self, user: User, data: ChatRequest) -> ChatResponse:
        # 1. 최근 5턴 가져오기 (슬라이딩 윈도우)
        recent = await self.repo.get_recent_conversations(user.id)

        # 2. 메시지 컨텍스트 조립
        messages = []
        for conv in recent:
            messages.append({"role": "user", "content": conv.encrypted_content})
            messages.append({"role": "model", "content": conv.encrypted_ai_response})
        messages.append({"role": "user", "content": data.message})

        # 3. AI 호출
        ai_response_raw = await AIClient.chat(messages, SYSTEM_PROMPT)

        # 4. 감정 점수 파싱
        ai_response, emotion_scores = self._parse_response(ai_response_raw)

        # 5. 대화 저장
        conversation = await self.repo.save_conversation(
            user_id=user.id,
            content=data.message,
            fixed_content=None,
            ai_response=ai_response,
        )
        # 6. 감정 점수 저장
        if emotion_scores:
            await self.emotion_repo.save_emotion(
                user_id=user.id,
                conversation_id=conversation.id,
                scores=emotion_scores,
            )

        return ChatResponse(
            id=conversation.id,
            message=ai_response,
            created_at=conversation.created_at,
        )

    @staticmethod
    def _parse_response(raw: str) -> tuple[str, dict]:
        import re, json
        pattern = r'\[EMOTION_SCORE\](.*?)\[/EMOTION_SCORE\]'
        match = re.search(pattern, raw, re.DOTALL)

        if match:
            emotion_json = match.group(1).strip()
            emotion_scores = json.loads(emotion_json)
            ai_response = raw[:raw.find('[EMOTION_SCORE]')].strip()
        else:
            emotion_scores = {}
            ai_response = raw.strip()

        return ai_response, emotion_scores