from enum import Enum
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"

class SubscriptionType(str, Enum):
    NONE = "none"
    STANDART = "standart"
    PREMIUM = "premium"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.AGENT, nullable=False)
    
    subscription: Mapped[SubscriptionType] = mapped_column(default=SubscriptionType.NONE, nullable=False)
    subscription_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    properties: Mapped[List["Property"]] = relationship(
        "Property", back_populates="agent", cascade="all, delete-orphan"
    )
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", back_populates="agent", cascade="all, delete-orphan"
    )

    def is_subscribed(self) -> bool:
        if self.role == UserRole.ADMIN:
            return True
        if self.subscription == SubscriptionType.NONE:
            return False
        if self.subscription_end and self.subscription_end < datetime.now(self.subscription_end.tzinfo):
            return False
        return True

    def __repr__(self) -> str:
        return f"<User {self.full_name} (Role: {self.role.value}, Sub: {self.subscription.value})>"
