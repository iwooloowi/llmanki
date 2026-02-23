import pytest

from llmanki.config import Settings, validate_settings


def test_validate_settings_missing_required_fields():
    settings = Settings(
        telegram_bot_token="",
        openai_api_key="",
        openai_model="gpt-4.1-mini",
        anki_connect_url="http://127.0.0.1:8765",
        db_path="./llmanki.sqlite",
        daily_quota=20,
        cooldown_seconds=10,
        max_regenerations=3,
    )

    with pytest.raises(ValueError):
        validate_settings(settings)
