from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.AGENT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Əlaqələr (Relationships)
    properties: Mapped[List["Property"]] = relationship(
        "Property", back_populates="agent", cascade="all, delete-orphan"
    )
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.full_name} (Role: {self.role.value})>"
