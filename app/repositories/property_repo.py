from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Property, PropertyStatus
from app.repositories.base import BaseRepository


class PropertyRepository(BaseRepository[Property]):
    def __init__(self):
        super().__init__(Property)

    async def get_by_agent(self, db: AsyncSession, agent_id: int, skip: int = 0, limit: int = 10) -> List[Property]:
        stmt = select(self.model).where(self.model.agent_id == agent_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def search_properties(
        self, db: AsyncSession, 
        district: Optional[str] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None,
        status: Optional[PropertyStatus] = None,
        skip: int = 0, limit: int = 10
    ) -> List[Property]:
        
        stmt = select(self.model)
        
        if district:
            stmt = stmt.where(self.model.district.ilike(f"%{district}%"))
        if min_price is not None:
            stmt = stmt.where(self.model.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(self.model.price <= max_price)
        if status:
            stmt = stmt.where(self.model.status == status)
            
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

property_repo = PropertyRepository()
