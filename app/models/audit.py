from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    """
    Sistemdə baş verən bütün mühüm əməliyyatların (Audit) tarixçəsi.
    Məsələn: 'Agent 123 tərəfindən 5 ID-li Ev satıldı'.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Əməliyyatı edən istifadəçi (Agent/Admin/Manager)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # CREATE, UPDATE, DELETE, STATUS_CHANGE
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # PROPERTY, CUSTOMER, USER
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Əməliyyatın detalları JSON formatında saxlanılır (Köhnə status, yeni status və s.)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.entity_type} {self.entity_id}>"
