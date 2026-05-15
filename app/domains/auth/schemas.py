from pydantic import BaseModel

#-------요청
class LocalRegisterRequest(BaseModel):
    name: str
    password: str
    email: str

class LocalLoginRequest(BaseModel):
    email: str
    password: str

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