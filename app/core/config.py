from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DATABASE_URL: str

    # AI Providers
    OPENAI_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

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


# Qlobal settings obyekti
settings = Settings()  # type: ignore
