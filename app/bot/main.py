import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# App konfiqurasiyası
from app.core.config import settings

# Routerlər
from app.bot.handlers.common import router as common_router
from app.bot.handlers.property import router as property_router
from app.bot.handlers.customer import router as customer_router
from app.bot.handlers.admin import router as admin_router

# Middlewarelər
from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.middlewares.auth import AuthMiddleware

# Database
from app.database.session import engine
from app.database.base import Base

# Bütün modelləri import edirik ki, Base.metadata onları görsün
from app.models.user import User
from app.models.property import Property
from app.models.customer import Customer
from app.models.audit import AuditLog

# Logging formatı
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def init_models():
    """Verilənlər bazasında cədvəlləri avtomatik yaradır (əgər yoxdursa)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    logger.info("Cədvəllər yoxlanılır və yaradılır...")
    try:
        await init_models()
        logger.info("Cədvəllər uğurla yoxlanıldı!")
    except Exception as e:
        logger.error(f"Cədvəl yaratmada xəta: {e}")

    logger.info("Bot işə düşür...")
    
    # Bot yaradılması
    bot = Bot(
        token=settings.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Dispatcher yaradılması (FSM default olaraq MemoryStorage işlədir)
    dp = Dispatcher()
    
    # Middleware-lərin qeydiyyatı (Sıra önəmlidir: Öncə DB, sonra Auth)
 #   dp.update.outer_middleware(DbSessionMiddleware())
 #   dp.update.outer_middleware(AuthMiddleware())
    
    # Routerlərin qeydiyyatı
    dp.include_router(common_router)
    dp.include_router(property_router)
    dp.include_router(customer_router)
    dp.include_router(admin_router)
    
    # Start polling
    try:
        # Əgər webhook qalıbsa, təmizləyirik ki polling işləyə bilsin
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot xətası: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
