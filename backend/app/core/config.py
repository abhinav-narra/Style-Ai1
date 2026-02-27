from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default="ai-fashion-stylist", alias="APP_NAME")
    app_env: Literal["dev", "prod"] = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_path: str = Field(
        default=str(Path("backend") / "data" / "app.db"),
        alias="DATABASE_PATH",
    )

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    jwt_secret: str = Field(default="dev-secret-change-me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    unsplash_access_key: str | None = Field(default=None, alias="UNSPLASH_ACCESS_KEY")
    pexels_api_key: str | None = Field(default=None, alias="PEXELS_API_KEY")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        data = {
            "APP_NAME": os.getenv("APP_NAME", "ai-fashion-stylist"),
            "APP_ENV": os.getenv("APP_ENV", "dev"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "DATABASE_PATH": os.getenv("DATABASE_PATH", str(Path("backend") / "data" / "app.db")),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "GROQ_MODEL": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "UNSPLASH_ACCESS_KEY": os.getenv("UNSPLASH_ACCESS_KEY"),
            "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY"),
        }
        _settings = Settings.model_validate(data)
    return _settings

