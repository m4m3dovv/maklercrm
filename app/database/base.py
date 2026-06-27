from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    """
    SQLAlchemy üçün təməl (Base) sinif.
    Bütün modellər bu sinifdən törəyəcək.
    """
    pass


class TimestampMixin:
    """
    Modellərə avtomatik created_at və updated_at sütunlarını əlavə edir.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
