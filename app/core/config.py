"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = "Reading List API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/readinglist"
    )
    db_echo: bool = False

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Pagination
    default_limit: int = 50
    max_limit: int = 100


settings = Settings()
