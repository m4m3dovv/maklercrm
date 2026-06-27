from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class PropertyStatus(str, Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    RENTED = "rented"
    SOLD = "sold"

class PropertyType(str, Enum):
    BINA_EVI = "Bina evi"
    HEYET_EVI = "Həyət evi / Bağ evi"
    TORPAQ = "Torpaq sahəsi"
    OBYEKT = "Obyekt / Ofis"

class DealType(str, Enum):
    SATIS = "Satılır"
    KIRAYE = "Kirayə verilir"

class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    property_type: Mapped[PropertyType] = mapped_column(default=PropertyType.BINA_EVI, index=True)
    deal_type: Mapped[DealType] = mapped_column(default=DealType.SATIS, index=True)
    
    price: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    room_count: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area: Mapped[float] = mapped_column(Float, nullable=False)
    
    district: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    settlement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    
    owner_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    document_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    status: Mapped[PropertyStatus] = mapped_column(
        default=PropertyStatus.ACTIVE, index=True, nullable=False
    )
    
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    agent: Mapped["User"] = relationship("User", back_populates="properties")
    interested_customers: Mapped[List["Customer"]] = relationship(
        "Customer", secondary="customer_property_association", back_populates="interested_properties"
    )

    def __repr__(self) -> str:
        return f"<Property {self.id} - {self.deal_type.value} {self.property_type.value}>"
