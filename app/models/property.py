from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin


class PropertyStatus(str, Enum):
    ACTIVE = "active"          # Aktiv
    RESERVED = "reserved"      # Rezerv edildi
    RENTED = "rented"          # Kirayə verildi
    SOLD = "sold"              # Satıldı


class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    price: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    room_count: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area: Mapped[float] = mapped_column(Float, nullable=False) # Kvadrat metr
    
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    settlement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # JSON sütunları - şəkil və video linklərini və ya fayl ID-lərini saxlamaq üçün (PostgreSQL JSONB kimi yaradacaq)
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Məsələn: CSV formatında və ya JSON formatında text
    video: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    status: Mapped[PropertyStatus] = mapped_column(
        default=PropertyStatus.ACTIVE, index=True, nullable=False
    )
    
    # Foreign Key (Evi idarə edən agent)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Əlaqələr
    agent: Mapped["User"] = relationship("User", back_populates="properties")
    interested_customers: Mapped[List["Customer"]] = relationship(
        "Customer", secondary="customer_property_association", back_populates="interested_properties"
    )

    def __repr__(self) -> str:
        return f"<Property {self.id} - {self.title} ({self.status.value})>"
