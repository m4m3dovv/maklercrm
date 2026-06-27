from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser, Message
from app.services.auth_service import AuthService

class AuthMiddleware(BaseMiddleware):
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

        try:
            # Sizi bazaya yazmağa / tapmağa çalışır
            actor = await AuthService.get_or_create_user(
                db=db,
                telegram_id=tg_user.id,
                full_name=tg_user.full_name,
                username=tg_user.username
            )
            data["actor"] = actor
            return await handler(event, data)
            
        except Exception as e:
            # XƏTANIN TƏFƏRRÜATINI TELEGRAMA GÖNDƏRİRİK
            if isinstance(event, Message):
                await event.answer(f"🚨 <b>Verilənlər Bazasında Xəta baş verdi:</b>\n\n<code>{str(e)}</code>", parse_mode="HTML")
            return None
