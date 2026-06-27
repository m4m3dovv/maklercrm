# Alembic-in bazaları görə bilməsi üçün bütün modellər buradan import olunmalıdır
from app.database.base import Base
from app.models.user import User
from app.models.property import Property
from app.models.customer import Customer
from app.models.audit import AuditLog

__all__ = ["Base", "User", "Property", "Customer", "AuditLog"]
