from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

# Çoxun-çoxa əlaqə üçün assosiativ cədvəl (Müştəri və Maraqlandığı evlər)
customer_property_association = Table(
    "customer_property_association",
    Base.metadata,
    Column("customer_id", Integer, ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True),
    Column("property_id", Integer, ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True),
)


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign Key (Müştərini əlavə edən agent)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Əlaqələr
    agent: Mapped["User"] = relationship("User", back_populates="customers")
    interested_properties: Mapped[List["Property"]] = relationship(
        "Property", secondary=customer_property_association, back_populates="interested_customers"
    )

    def __repr__(self) -> str:
        return f"<Customer {self.full_name} - Phone: {self.phone}>"
