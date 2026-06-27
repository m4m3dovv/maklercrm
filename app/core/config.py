from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str

    # Database
    DATABASE_URL: str
    
    # Biz artıq Pydantic-in bunlara görə xəta verməsini istəmirik
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DB: Optional[str] = None

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Application Settings
    ADMIN_IDS: str  # Comma separated list of admin telegram IDs
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(id_str.strip()) for id_str in self.ADMIN_IDS.split(",") if id_str.strip().isdigit()]

settings = Settings()  # type: ignore
