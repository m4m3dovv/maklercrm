from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self):
        super().__init__(Customer)

    async def get_by_agent(self, db: AsyncSession, agent_id: int, skip: int = 0, limit: int = 10) -> List[Customer]:
        stmt = select(self.model).where(self.model.agent_id == agent_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_interested_properties(self, db: AsyncSession, customer_id: int) -> Optional[Customer]:
        # Eager loading with selectinload to load the many-to-many relationship
        stmt = select(self.model).options(selectinload(self.model.interested_properties)).where(self.model.id == customer_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_customers(self, db: AsyncSession, phone: Optional[str] = None, name: Optional[str] = None) -> List[Customer]:
        stmt = select(self.model)
        if phone:
            stmt = stmt.where(self.model.phone.ilike(f"%{phone}%"))
        if name:
            stmt = stmt.where(self.model.full_name.ilike(f"%{name}%"))
            
        result = await db.execute(stmt)
        return list(result.scalars().all())

customer_repo = CustomerRepository()
