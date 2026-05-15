from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domains.auth.repository import AuthRepository
from app.domains.auth.service import AuthService
from app.domains.auth.schemas import LocalRegisterRequest, UserResponse, LocalLoginRequest, TokenResponse


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