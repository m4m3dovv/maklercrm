from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.property import PropertyStatus


# --- PROPERTY SCHEMAS ---
class PropertyBase(BaseModel):
    title: str = Field(..., max_length=150)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    room_count: int = Field(..., gt=0)
    floor: Optional[int] = None
    area: float = Field(..., gt=0)
    district: str = Field(..., max_length=100)
    settlement: Optional[str] = Field(None, max_length=100)
    address: str = Field(..., max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[str] = None
    video: Optional[str] = None
    status: PropertyStatus = PropertyStatus.ACTIVE


class PropertyCreate(PropertyBase):
    agent_id: int


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    room_count: Optional[int] = Field(None, gt=0)
    floor: Optional[int] = None
    area: Optional[float] = Field(None, gt=0)
    district: Optional[str] = Field(None, max_length=100)
    settlement: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[str] = None
    video: Optional[str] = None
    status: Optional[PropertyStatus] = None


class PropertyResponse(PropertyBase):
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
