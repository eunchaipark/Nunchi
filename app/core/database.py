from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_sessionmaker, AsyncSession
from app.config.settings import settings

# 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)
# 세션팩토리 생성 -> 엔진에 묶어두고 비동기 세션, 커밋해도 객체 남겨둔다 -> 운영 단계에서는 객체 제거 해야함
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

#
async def get_db() :
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
