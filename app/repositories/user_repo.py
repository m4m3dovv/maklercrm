from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> Optional[User]:
        stmt = select(self.model).where(self.model.telegram_id == telegram_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_agents(self, db: AsyncSession):
        stmt = select(self.model).where(
            self.model.is_active == True,
            self.model.role == UserRole.AGENT
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

user_repo = UserRepository()
