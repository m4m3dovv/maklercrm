from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.database.session import async_session_maker


class DbSessionMiddleware(BaseMiddleware):
    """
    Hər bir Telegram update-i üçün yeni AsyncSession yaradır 
    və handler-ə `db` adlı arqument kimi ötürür.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            data["db"] = session
            # DB session hazır olduqdan sonra digər handler-lərə keçid edirik
            return await handler(event, data)
