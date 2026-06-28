from typing import Callable, Dict, Any, Awaitable
import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser, Message, CallbackQuery
from app.services.auth_service import AuthService
from app.models.user import UserRole

logger = logging.getLogger(__name__)

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
            raise ValueError("DB session tapılmadı.")

        try:
            actor = await AuthService.get_or_create_user(
                db=db,
                telegram_id=tg_user.id,
                full_name=tg_user.full_name,
                username=tg_user.username
            )
            data["actor"] = actor
            
            # ƏGƏR ADMIN DEYİLSƏ VƏ ABUNƏLİYİ YOXDURSA BOTU İŞLƏTMƏYƏ İCAZƏ VERMİRİK
            message_text = getattr(event, "text", "")
            
            # /start, /make_me_admin, /pay (ödəniş komandaları) keçidə icazəlidir
            allowed_commands = ["/start", "/make_me_admin", "💳 Abunə ol"]
            if actor.role != UserRole.ADMIN and not actor.is_subscribed():
                if isinstance(event, Message) and not any(cmd in message_text for cmd in allowed_commands if message_text):
                    from aiogram.utils.keyboard import ReplyKeyboardBuilder
                    kb = ReplyKeyboardBuilder()
                    kb.button(text="💳 Abunə ol")
                    await event.answer("⚠️ <b>Sizin aktiv abunəliyiniz yoxdur.</b>\n\n"
                                       "Sistemdən istifadə etmək və evlər əlavə etmək üçün paket almalısınız.",
                                       reply_markup=kb.as_markup(resize_keyboard=True), parse_mode="HTML")
                    return None # Botu burada dondurur
                    
                if isinstance(event, CallbackQuery) and "pay_" not in event.data:
                    await event.answer("⚠️ Aktiv abunəliyiniz yoxdur!", show_alert=True)
                    return None
            
            return await handler(event, data)
            
        except Exception as e:
            if isinstance(event, Message):
                await event.answer(f"🚨 <b>Verilənlər Bazasında Xəta baş verdi:</b>\n\n<code>{str(e)}</code>", parse_mode="HTML")
            return None
