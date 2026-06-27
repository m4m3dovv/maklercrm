from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.property import Property, PropertyStatus
from app.models.user import User, UserRole
from app.repositories.property_repo import property_repo
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.core.exceptions import NotFoundException, PermissionDeniedException

class PropertyService:
    @staticmethod
    async def create_property(db: AsyncSession, data: PropertyCreate, actor: User) -> Property:
        # İstənilən agent ev yarada bilər
        property_data = data.model_dump()
        property_data["agent_id"] = actor.id
        return await property_repo.create(db, property_data)

    @staticmethod
    async def get_property(db: AsyncSession, property_id: int) -> Property:
        prop = await property_repo.get_by_id(db, property_id)
        if not prop:
            raise NotFoundException("Ev")
        return prop

    @staticmethod
    async def change_status(db: AsyncSession, property_id: int, new_status: PropertyStatus, actor: User) -> Property:
        prop = await PropertyService.get_property(db, property_id)
        
        # Yalnız evin agenti, admin və ya manager statusu dəyişə bilər
        if actor.role == UserRole.AGENT and prop.agent_id != actor.id:
            raise PermissionDeniedException()
            
        return await property_repo.update(db, prop, {"status": new_status})
    
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
