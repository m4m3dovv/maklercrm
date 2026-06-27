import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings
from app.bot.handlers.common import router as common_router
from app.bot.handlers.property import router as property_router
from app.bot.handlers.customer import router as customer_router
from app.bot.handlers.admin import router as admin_router

from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.middlewares.auth import AuthMiddleware

from app.database.session import engine
from app.database.base import Base

# Modelləri import edirik ki, cədvəlləri tanıya bilsin
from app.models.user import User
from app.models.property import Property
from app.models.customer import Customer
from app.models.audit import AuditLog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ÇOX VACİB: Cədvəlləri sıfırlayıb (Drop) yenidən yaradır (Create)
async def init_models():
    async with engine.begin() as conn:
        logger.info("Köhnə cədvəllər silinir...")
        await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Yeni sütunlarla birlikdə cədvəllər yaradılır...")
        await conn.run_sync(Base.metadata.create_all)

async def main():
    logger.info("Sistem başlanır...")
    
    try:
        await init_models()
        logger.info("Baza uğurla yeniləndi və hazır vəziyyətə gətirildi!")
    except Exception as e:
        logger.error(f"Baza yenilənməsində xəta: {e}")

    bot = Bot(
        token=settings.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.outer_middleware(AuthMiddleware())
    
    dp.include_router(common_router)
    dp.include_router(property_router)
    dp.include_router(customer_router)
    dp.include_router(admin_router)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Polling xətası: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
