from __future__ import annotations

from telegram.ext import Application

from llmanki.bot.handlers import build_handlers
from llmanki.config import Settings
from llmanki.services.anki_connect import AnkiConnectClient
from llmanki.services.deck_manager import DeckManager
from llmanki.services.example_generator import ExampleGenerator
from llmanki.services.llm_client import LLMClient
from llmanki.storage.db import connect, init_db
from llmanki.storage.repositories import PendingRepository, UserRepository


def build_application(settings: Settings) -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()

    conn = connect(settings.db_path)
    init_db(conn)

    user_repo = UserRepository(conn)
    pending_repo = PendingRepository(conn)

    llm = LLMClient(api_key=settings.openai_api_key, model=settings.openai_model)
    generator = ExampleGenerator(llm)

    anki = AnkiConnectClient(settings.anki_connect_url)
    deck_manager = DeckManager(anki)

    app.bot_data["settings"] = settings
    app.bot_data["user_repo"] = user_repo
    app.bot_data["pending_repo"] = pending_repo
    app.bot_data["example_generator"] = generator
    app.bot_data["deck_manager"] = deck_manager

    for h in build_handlers():
        app.add_handler(h)

    return app
