from __future__ import annotations

from dotenv import load_dotenv

import asyncio

from llmanki.bot.app import build_application
from llmanki.config import load_settings, validate_settings
from llmanki.logging import setup_logging
from llmanki.services.anki_connect import AnkiConnectClient, AnkiConnectError


def main() -> None:
    load_dotenv()
    setup_logging()
    settings = load_settings()
    validate_settings(settings)
    try:
        asyncio.run(AnkiConnectClient(settings.anki_connect_url).version())
    except AnkiConnectError as exc:
        raise SystemExit(str(exc)) from exc
    app = build_application(settings)
    app.run_polling()


if __name__ == "__main__":
    main()
