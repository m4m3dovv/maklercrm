from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

# Async Engine yaradılması (Echo=False production üçün)
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Başıboş connectionları təmizləmək üçün
    pool_size=10,
    max_overflow=20
)

# Async Session Maker yaradılması
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Hər asinxron əməliyyat (request/update) üçün session qaytarır.
    Context Manager kimi istifadə olunur.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
