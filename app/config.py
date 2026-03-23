from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Users API"
    app_version: str = "1.0.0"
    app_description: str = "API for managing users"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/users_db",
        alias="DATABASE_URL"
    )

    redis_url: str = Field(
        default="redis://cache:6379",
        alias="REDIS_URL"
    )
    redis_cache_ttl: int = Field(
        default=60 * 60 * 24, # 24 hours
        alias="REDIS_CACHE_TTL"
    )

    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
   