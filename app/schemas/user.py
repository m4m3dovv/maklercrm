from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, SubscriptionType

class UserBase(BaseModel):
    telegram_id: int
    full_name: str = Field(..., max_length=100)
    username: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.AGENT
    subscription: SubscriptionType = SubscriptionType.NONE
    subscription_end: Optional[datetime] = None
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    subscription: Optional[SubscriptionType] = None
    subscription_end: Optional[datetime] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
