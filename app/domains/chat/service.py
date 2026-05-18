from fastapi import HTTPException

from app.core.ai_client import AIClient
from app.core.security import decode_pin_token, decrypt, encrypt
from app.domains.chat.repository import ChatRepository
from app.domains.chat.schemas import ChatRequest, ChatResponse
from app.domains.emotion.repository import EmotionRepository
from app.domains.notification.repository import NotificationRepository
from app.domains.notification.service import NotificationService
from app.domains.user.models import User
from app.domains.usage.repository import UsageRepository
from app.domains.usage.service import UsageService

SYSTEM_PROMPT = """
당신은 따뜻한 말벗이 되어주는 AI입니다.
상대방의 말씀을 경청하고 공감하며 대화를 이어나가세요.
방언이나 오타가 있어도 문맥으로 이해하고 자연스럽게 대화하세요.

대화 규칙:
1. 짧고 친근하게 답변하세요 (2~3문장)
2. 반드시 질문으로 대화를 이어가세요
3. 상대방의 감정에 먼저 공감한 후 질문하세요
4. 현실적으로 불가능한 말은 하지 마세요 (예: "같이 먹어요", "제가 도와드릴게요" 등)
5. 상대방의 성별, 나이, 호칭을 임의로 가정하지 마세요
6. 특정 호칭 대신 "그러셨군요", "어떠세요?" 처럼 중립적인 표현을 사용하세요

반드시 아래 형식으로 응답하세요:

[FIXED]
(입력 문장의 오타/방언을 교정한 텍스트. 교정할 것이 없으면 원문 그대로)
[/FIXED]

[RESPONSE]
(대화 응답)
[/RESPONSE]

[EMOTION_SCORE]
{"loneliness": 0~10, "anxiety": 0~10, "depression": 0~10, "vitality": 0~10, "connection": 0~10, "hope": 0~10}
[/EMOTION_SCORE]
"""


class ChatService:
    def __init__(
        self,
        repo: ChatRepository,
        emotion_repo: EmotionRepository,
        notification_repo: NotificationRepository,
        usage_repo: UsageRepository
    ):
        self.repo = repo
        self.emotion_repo = emotion_repo
        self.notification_repo = notification_repo
        self.usage_repo = usage_repo

    async def chat(self, user: User, data: ChatRequest) -> ChatResponse:

        # 글자 수 체크
        if not data.voice_seconds and len(data.message) > 0:
            plan = await self.usage_repo.get_plan(user.id)
            if plan and len(data.message) > plan.text_max_length:
                raise HTTPException(
                    status_code=400,
                    detail=f"텍스트는 {plan.text_max_length}자 이하로 입력해주세요"
                )

        # 사용량 체크
        usage_service = UsageService(self.usage_repo)
        quota = await usage_service.check_quota(user.id, data.voice_seconds)
        if not quota.can_use:
            raise HTTPException(status_code=429, detail=quota.reason)

        try:
            pin = decode_pin_token(data.pin_token)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=401, detail=str(e))

        # 1. 최근 5턴 가져오기 (슬라이딩 윈도우)
        recent = await self.repo.get_recent_conversations(user.id)

        # 2. 메시지 컨텍스트 조립 --> 복호화 해서 AI.에 전달
        messages = []
        for conv in recent:
            try:
                content = decrypt(conv.encrypted_content, pin)
                ai_resp = decrypt(conv.encrypted_ai_response, pin)
            except Exception as e:
                content = conv.encrypted_content
                ai_resp = conv.encrypted_ai_response
            messages.append({"role": "user", "content": content})
            messages.append({"role": "model", "content": ai_resp})
        messages.append({"role": "user", "content": data.message})

        #  AI 호출
        ai_response_raw = await AIClient.chat(messages, SYSTEM_PROMPT)

        #  파싱
        ai_response, fixed_content, emotion_scores = ChatService._parse_response(ai_response_raw)

        # 암호화 해서 저장
        encrypt_content = encrypt(data.message, pin)
        encrypted_fixed = encrypt(fixed_content, pin) if fixed_content else None
        encrypt_ai_response = encrypt(ai_response, pin)

        #  대화 저장
        conversation = await self.repo.save_conversation(
            user_id=user.id,
            content=encrypt_content,
            fixed_content=encrypted_fixed,
            ai_response=encrypt_ai_response,
        )

        #  감정 점수 저장
        if emotion_scores:
            saved_emotion = await self.emotion_repo.save_emotion(
                user_id=user.id,
                conversation_id=conversation.id,
                scores=emotion_scores,
            )
            # 7. 위험도 체크 후 알림
            notification_service = NotificationService(self.notification_repo)
            await notification_service.check_and_notify(user.id, saved_emotion.overall_risk)

        # 사용량 차감
        await usage_service.consume(user.id, data.voice_seconds)

        return ChatResponse(
            id=conversation.id,
            message=ai_response,
            created_at=conversation.created_at,
        )

    @staticmethod
    def _parse_response(raw: str) -> tuple[str, str, dict]:
        import re, json

        # 교정본 파싱
        fixed_match = re.search(r'\[FIXED\](.*?)\[/FIXED\]', raw, re.DOTALL)
        fixed_content = fixed_match.group(1).strip() if fixed_match else ""

        # 대화 응답 파싱
        response_match = re.search(r'\[RESPONSE\](.*?)\[/RESPONSE\]', raw, re.DOTALL)
        ai_response = response_match.group(1).strip() if response_match else raw.strip()

        # 감정 점수 파싱
        emotion_match = re.search(r'\[EMOTION_SCORE\](.*?)\[/EMOTION_SCORE\]', raw, re.DOTALL)
        if emotion_match:
            emotion_scores = json.loads(emotion_match.group(1).strip())
        else:
            emotion_scores = {}

        return ai_response, fixed_content, emotion_scores
