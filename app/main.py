from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine
from app.domains.auth.controller import router as auth_router
from app.domains.chat.controller import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작
    async with engine.begin() as conn:
        print("DB 연결 성공!")
    yield
    # 종료
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)   #회원가입

app.include_router(chat_router)  # CHAT


@app.get("/")
async def root():
    return {"message": "Nunchi API"}