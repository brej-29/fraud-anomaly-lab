from functools import lru_cache

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "info"

    environment: str = "local"

    dashboard_url: AnyHttpUrl | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of settings."""
    return Settings()