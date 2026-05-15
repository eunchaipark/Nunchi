from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domains.user.models import User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 비동기 함수이고 init에서 자기 자신(self)에게 저장해둔 세션을 꺼내 쓴다
    # str타입의 이메일을 입력해서 반환타입의 힌트는 User객체 혹은 None
    # select(User)는 sql로 치면 select * from user
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    #
    async def create_user(self, email: str, password_hash: str, name: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
        )
        self.db.add(user)  # 세션에 객체를 등록한다 즉 DB에 넣을 준비를 해라
        await self.db.flush() #세션에 등록된 변경 사항을 DB에 즉시 반영 (커밋이 아니다)
        return user
