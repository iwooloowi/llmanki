from typing import cast

import pytest
from telegram import Update

from llmanki.storage.db import connect, init_db
from llmanki.storage.repositories import UserRepository


class DummyMessage:
    def __init__(self):
        self.sent = []

    async def reply_text(self, text, reply_markup=None):
        self.sent.append((text, reply_markup))


class DummyUser:
    def __init__(self, user_id):
        self.id = user_id


class DummyUpdate:
    def __init__(self, user_id):
        self.effective_user = DummyUser(user_id)
        self.message = DummyMessage()


class DummyApp:
    def __init__(self, bot_data):
        self.bot_data = bot_data


class DummyContext:
    def __init__(self, bot_data):
        self.application = DummyApp(bot_data)


@pytest.mark.asyncio
async def test_status_command_reports_quota_and_deck(tmp_path):
    conn = connect(str(tmp_path / "t.sqlite"))
    init_db(conn)
    user_repo = UserRepository(conn)
    user_repo.set_deck(1, "MyDeck")

    update = DummyUpdate(user_id=1)
    context = DummyContext(
        {
            "user_repo": user_repo,
            "settings": type("S", (), {"daily_quota": 20, "cooldown_seconds": 10})(),
        }
    )

    from llmanki.bot.commands import status

    await status(cast(Update, update), context)

    assert update.message is not None
    assert update.message.sent
    text, _ = update.message.sent[-1]
    assert "Deck: MyDeck" in text
    assert "Daily remaining: 20" in text
