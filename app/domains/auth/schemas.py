from pydantic import BaseModel

#-------요청
class LocalRegisterRequest(BaseModel):
    name: str
    password: str
    email: str

class LocalLoginRequest(BaseModel):
    email: str
    password: str

# 복호화를 위한 4자리
class PinSetRequest(BaseModel):
    pin: str

# --------응답
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str | None = None
    kakao_id : str | None = None
    has_pin: bool

    class Config:
        from_attributes = True

# ----- 회원 탈퇴 요청
class DeleteAccountRequest(BaseModel):
    password: str

# -------비밀번호 변경
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

#-------pin 검증
class PinVerifyRequest(BaseModel):
    pin: str

class PinTokenResponse(BaseModel):
    pin_token: str
    message: str