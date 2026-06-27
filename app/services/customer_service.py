from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.customer import Customer
from app.models.user import User, UserRole
from app.repositories.customer_repo import customer_repo
from app.schemas.customer import CustomerCreate
from app.core.exceptions import NotFoundException, PermissionDeniedException


class CustomerService:
    @staticmethod
    async def create_customer(db: AsyncSession, data: CustomerCreate, actor: User) -> Customer:
        customer_data = data.model_dump()
        customer_data["agent_id"] = actor.id
        return await customer_repo.create(db, customer_data)
        
    @staticmethod
    async def get_customer(db: AsyncSession, customer_id: int, actor: User) -> Customer:
        customer = await customer_repo.get_by_id(db, customer_id)
        if not customer:
            raise NotFoundException("Müştəri")
            
        # Agent yalnız öz müştərisini görə bilər (Admin və Manager hamısını görə bilər)
        if actor.role == UserRole.AGENT and customer.agent_id != actor.id:
            raise PermissionDeniedException()
            
        return customer
        
    @staticmethod
    async def assign_property_to_customer(db: AsyncSession, customer_id: int, property_id: int, actor: User):
        """Müştərinin maraqlandığı evlərə yeni ev əlavə edir"""
        from app.services.property_service import PropertyService
        
        customer = await customer_repo.get_with_interested_properties(db, customer_id)
        if not customer:
            raise NotFoundException("Müştəri")
            
        if actor.role == UserRole.AGENT and customer.agent_id != actor.id:
            raise PermissionDeniedException()
            
        prop = await PropertyService.get_property(db, property_id)
        
        # Əgər artıq siyahıda yoxdursa, əlavə et
        if not any(p.id == prop.id for p in customer.interested_properties):
            customer.interested_properties.append(prop)
            await db.commit()
            
        return customer
