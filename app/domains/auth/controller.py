from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import current_user

from app.core.database import get_db
from app.domains.auth.repository import AuthRepository
from app.domains.auth.service import AuthService
from app.domains.auth.schemas import LocalRegisterRequest, UserResponse, LocalLoginRequest, TokenResponse, \
    PinSetRequest, DeleteAccountRequest, ChangePasswordRequest, PinVerifyRequest, PinTokenResponse
from app.core.dependencies import get_current_user
from app.domains.user.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
        data: LocalRegisterRequest,
        db: AsyncSession = Depends(get_db)
):
    repo = AuthRepository(db)
    service = AuthService(repo)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
        data: LocalLoginRequest,
        db: AsyncSession = Depends(get_db)
):
    repo = AuthRepository(db)
    service = AuthService(repo)
    return await service.login(data)


@router.post("/pin")
async def set_pin(
    data: PinSetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = AuthRepository(db)
    service = AuthService(repo)
    return await service.set_pin(current_user, data)


@router.delete("/me")
async def delete_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = AuthRepository(db)
    service = AuthService(repo)
    return await service.delete_account(current_user, data)

@router.get("/me/password")
async def change_password(
        data:ChangePasswordRequest,
        current_user:User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = AuthRepository(db)
    service = AuthService(repo)
    return await service.change_password(current_user, data)


@router.post("/pin/verify", response_model=PinTokenResponse)
async def verify_pin(
        data: PinVerifyRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = AuthRepository(db)
    service = AuthService(repo)
    return await service.verify_pin(current_user, data)