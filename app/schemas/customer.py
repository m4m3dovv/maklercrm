from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# --- CUSTOMER SCHEMAS ---
class CustomerBase(BaseModel):
    full_name: str = Field(..., max_length=150)
    phone: str = Field(..., max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    budget: Optional[float] = Field(None, ge=0)
    district: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    agent_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    budget: Optional[float] = Field(None, ge=0)
    district: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    agent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
