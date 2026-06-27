from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.property import PropertyStatus, PropertyType, DealType

class PropertyBase(BaseModel):
    title: str = Field(..., max_length=150)
    description: Optional[str] = None
    property_type: PropertyType
    deal_type: DealType
    price: float = Field(..., gt=0)
    room_count: int = Field(..., ge=0)
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    area: float = Field(..., gt=0)
    district: str = Field(..., max_length=100)
    settlement: Optional[str] = Field(None, max_length=100)
    address: str = Field(..., max_length=255)
    owner_phone: Optional[str] = None
    document_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[str] = None
    video: Optional[str] = None
    status: PropertyStatus = PropertyStatus.ACTIVE

class PropertyCreate(PropertyBase):
    agent_id: int

class PropertyUpdate(BaseModel):
    pass
    
class PropertyResponse(PropertyBase):
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
