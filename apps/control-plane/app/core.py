import os

from pydantic import BaseModel, Field


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = "internal-developer-platform-control-plane"
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "local"))
    api_prefix: str = Field(default_factory=lambda: os.getenv("API_PREFIX", "/api/v1"))
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./control-plane.db")
    )
    db_echo: bool = Field(default_factory=lambda: _env_flag("DB_ECHO", False))
    db_required: bool = Field(default_factory=lambda: _env_flag("DB_REQUIRED", False))
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))


settings = Settings()
