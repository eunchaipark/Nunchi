from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext

from app.config.settings import settings
from app.core.security import create_pin_token
from app.domains.auth.repository import AuthRepository
from app.domains.auth.schemas import LocalRegisterRequest, LocalLoginRequest, UserResponse, TokenResponse, \
    PinSetRequest, DeleteAccountRequest, ChangePasswordRequest, PinVerifyRequest
from app.domains.user.models import User

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

    async def set_pin(self, user: User, data: PinSetRequest) -> dict:
        if not data.pin.isdigit() or len(data.pin) != 4:
            raise HTTPException(status_code=400, detail="PIN은 4자리 숫자여야 해요")
        hashed_pin = AuthService.hash_password(data.pin)
        await self.repo.update_pin(user.id, hashed_pin)
        return {"message": "PIN이 설정되었어요"}


    #----------회원 탈퇴
    async def delete_account(self,user:User, data: DeleteAccountRequest) -> dict:
        if not AuthService.verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="비밀번호가 틀렸어요")
        await self.repo.delete_user(user.id)
        return {"message": "탈퇴 되었습니다."}


    #---- 비밀번호 변경
    async def change_password(self, user:User, data: ChangePasswordRequest) -> dict:
        if not user.password_hash:
            raise HTTPException(status_code=400, detail="카카오 계정은 비밀번호를 바꿀수 없습니다.")
        if not AuthService.verify_password(data.current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="현재 비밀번호가 틀렸습니다")
        new_hashed = AuthService.hash_password(data.new_password)
        await self.repo.update_password(user.id, new_hashed)
        return {"message" : "비밀번호가 변경되었습니다."}

    #-----pin검증
    async def verify_pin(self, user: User, data: PinVerifyRequest) -> dict:
        if not user.has_pin:
            raise HTTPException(status_code=400, detail="Pin이 설정되지 않았습니다")
        if not AuthService.verify_password(data.pin, user.pin_hash):
            raise HTTPException(status_code=401, detail="Pin이 틀렸습니다")
        pin_token = create_pin_token(data.pin)
        return {"pin_token": pin_token, "message": "PIN 확인되었어요"}