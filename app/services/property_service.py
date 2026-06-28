from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.property import Property, PropertyStatus
from app.models.user import User, UserRole
from app.repositories.property_repo import property_repo
from app.schemas.property import PropertyCreate
from app.core.exceptions import NotFoundException, PermissionDeniedException

class PropertyService:
    @staticmethod
    async def create_property(db: AsyncSession, data: PropertyCreate, actor: User) -> Property:
        property_data = data.model_dump()
        property_data["agent_id"] = actor.id
        return await property_repo.create(db, property_data)

    @staticmethod
    async def get_property(db: AsyncSession, property_id: int) -> Property:
        prop = await property_repo.get_by_id(db, property_id)
        if not prop:
            raise NotFoundException("Əmlak")
        return prop

    @staticmethod
    async def change_status(db: AsyncSession, property_id: int, new_status: str, actor: User) -> Property:
        prop = await PropertyService.get_property(db, property_id)
        
        if actor.role == UserRole.AGENT and prop.agent_id != actor.id:
            raise PermissionDeniedException()
            
        if new_status == PropertyStatus.ACTIVE.value:
            status_enum = PropertyStatus.ACTIVE
        elif new_status == PropertyStatus.RESERVED.value:
            status_enum = PropertyStatus.RESERVED
        elif new_status == PropertyStatus.RENTED.value:
            status_enum = PropertyStatus.RENTED
        elif new_status == PropertyStatus.SOLD.value:
            status_enum = PropertyStatus.SOLD
        else:
            status_enum = PropertyStatus.ACTIVE 

        return await property_repo.update(db, prop, {"status": status_enum})
    
    @staticmethod
    async def search(
        db: AsyncSession, 
        district: Optional[str] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None,
        status: Optional[PropertyStatus] = None,
        skip: int = 0, limit: int = 10
    ) -> List[Property]:
        return await property_repo.search_properties(db, district, min_price, max_price, status, skip, limit)
