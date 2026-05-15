from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DB
    DATABASE_URL: str

    # AI
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""

    # 임베딩
    JINA_API_KEY: str = ""

    # 인증
    KAKAO_CLIENT_ID: str = ""
    KAKAO_REDIRECT_URI: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # 알림
    SENDGRID_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()