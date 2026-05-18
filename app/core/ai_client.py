import google.generativeai as genai
from app.config.settings import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


class AIClient:
    @staticmethod
    async def chat(messages: list[dict], system_prompt: str) -> str:
        history = []
        for msg in messages[:-1]:
            history.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })

        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(
            system_prompt + "\n\n" + messages[-1]["content"]
        )
        return response.text
