from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser
from app.services.auth_service import AuthService


class AuthMiddleware(BaseMiddleware):
    """
    İstifadəçini bazadan tapır (və ya yaradır) və `actor` kimi handler-ə ötürür.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        
        tg_user: TelegramUser | None = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)

        db = data.get("db")
        if not db:
            raise ValueError("DB session tapılmadı. DbSessionMiddleware əvvəl işləməlidir.")

        # İstifadəçini yoxla və ya yarat
        actor = await AuthService.get_or_create_user(
            db=db,
            telegram_id=tg_user.id,
            full_name=tg_user.full_name,
            username=tg_user.username
        )
        
        # Bütün handlerlərdə "actor" (istifadəçi obyekti) əlçatan olacaq
        data["actor"] = actor
        
        return await handler(event, data)
