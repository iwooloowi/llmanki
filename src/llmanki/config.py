from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str
    openai_model: str
    anki_connect_url: str
    db_path: str
    daily_quota: int
    cooldown_seconds: int
    max_regenerations: int


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
        openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip(),
        anki_connect_url=os.environ.get("ANKI_CONNECT_URL", "http://127.0.0.1:8765").strip(),
        db_path=os.environ.get("DB_PATH", "./llmanki.sqlite").strip(),
        daily_quota=int(os.environ.get("DAILY_QUOTA", "20")),
        cooldown_seconds=int(os.environ.get("COOLDOWN_SECONDS", "10")),
        max_regenerations=int(os.environ.get("MAX_REGENERATIONS", "3")),
    )


def validate_settings(settings: Settings) -> None:
    missing = []
    if not settings.telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not settings.openai_model:
        missing.append("OPENAI_MODEL")

    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")
