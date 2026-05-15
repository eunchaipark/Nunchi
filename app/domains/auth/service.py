from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext

from app.config.settings import settings
from app.domains.auth.repository import AuthRepository
from app.domains.auth.schemas import LocalRegisterRequest, LocalLoginRequest, UserResponse, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def _create_token(user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "exp": expire,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    async def register(self, data: LocalRegisterRequest) -> UserResponse:
        existing = await self.repo.get_user_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일이에요")
        hashed = AuthService.hash_password(data.password)
        user = await self.repo.create_user(
            email=data.email,
            password_hash=hashed,
            name=data.name,
        )
        return UserResponse.model_validate(user)

    async def login(self, data: LocalLoginRequest) -> TokenResponse:
        existing = await self.repo.get_user_by_email(data.email)
        if not existing:
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다.")
        if not existing.password_hash:
            raise HTTPException(status_code=401, detail="카카오 로그인 계정입니다.")
        if not AuthService.verify_password(data.password, existing.password_hash):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다.")

        token = AuthService._create_token(existing.id)
        return TokenResponse(access_token=token, token_type="bearer")