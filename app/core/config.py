import secrets
from typing import Any, Dict

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database Configuration
    # Default to SQLite for development, override with .env for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SQLITE_ASYNC_CONN_STR: str | None = None

    # Security
    # IMPORTANT: Use a strong, randomly generated secret in production.
    # Generate one using: openssl rand -hex 32 or secrets.token_hex(32)
    # Store this persistent key in your .env file or environment variables.
    SECRET_KEY: str = secrets.token_hex(32)

    @model_validator(mode="before")
    @classmethod
    def set_sqlite_async_conn_str(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set SQLite connection string for compatibility if using SQLite."""
        database_url = values.get("DATABASE_URL", "")
        if "sqlite+aiosqlite" in database_url:
            # Ensure proper SQLite async connection format
            if not database_url.startswith("sqlite+aiosqlite:///./"):
                values["SQLITE_ASYNC_CONN_STR"] = database_url.replace(
                    "sqlite+aiosqlite:///",
                    "sqlite+aiosqlite:///./",
                )
            else:
                values["SQLITE_ASYNC_CONN_STR"] = database_url
        return values

    @property
    def is_sqlite(self) -> bool:
        """Check if the current database is SQLite."""
        return "sqlite" in self.DATABASE_URL.lower()

    @property
    def is_postgresql(self) -> bool:
        """Check if the current database is PostgreSQL."""
        return "postgresql" in self.DATABASE_URL.lower()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
