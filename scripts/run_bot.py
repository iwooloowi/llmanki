from __future__ import annotations

from dotenv import load_dotenv

from llmanki.bot.app import build_application
from llmanki.config import load_settings
from llmanki.logging import setup_logging


def main() -> None:
    load_dotenv()
    setup_logging()
    settings = load_settings()
    app = build_application(settings)
    app.run_polling()


if __name__ == "__main__":
    main()
