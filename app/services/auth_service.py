from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.user import User, UserRole
from app.repositories.user_repo import user_repo
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import NotFoundException, PermissionDeniedException


class AuthService:
    @staticmethod
    async def get_or_create_user(
        db: AsyncSession, 
        telegram_id: int, 
        full_name: str, 
        username: Optional[str] = None
    ) -> User:
        """
        İstifadəçi varsa gətirir, yoxdursa yeni Agent kimi yaradır.
        """
        user = await user_repo.get_by_telegram_id(db, telegram_id)
        if not user:
            user_data = UserCreate(
                telegram_id=telegram_id,
                full_name=full_name,
                username=username,
                role=UserRole.AGENT  # Default olaraq hamı Agent olur, adminlər sonradan təyin edir
            )
            user = await user_repo.create(db, user_data.model_dump())
        
        # Əgər telegram username dəyişibsə yenilə
        elif user.username != username or user.full_name != full_name:
            await user_repo.update(db, user, {"username": username, "full_name": full_name})
            
        return user

    @staticmethod
    def check_is_admin(user: User):
        if user.role != UserRole.ADMIN:
            raise PermissionDeniedException()

    @staticmethod
    def check_is_manager_or_admin(user: User):
        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise PermissionDeniedException()
