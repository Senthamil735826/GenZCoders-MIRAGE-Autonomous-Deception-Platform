from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    APP_NAME: str = "MIRAGE Autonomous Deception Platform"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./mirage.db"
    SQL_ECHO: bool = False

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    THREAT_SCORE_ALERT_THRESHOLD: int = 70
    MAX_INTERACTIONS_PER_MINUTE: int = 30

    GEMINI_API_KEY: SecretStr | None = None
    ABUSEIPDB_API_KEY: SecretStr | None = None

    MIRAGE_API_KEY: SecretStr = SecretStr("dev-local-key-change-me")

    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"

    DRY_RUN: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()