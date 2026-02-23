import pytest

from llmanki.bot.conversations import State
from llmanki.domain.models import Generation
from llmanki.storage.db import connect, init_db
from llmanki.storage.repositories import PendingRepository, UserRepository


class DummyMessage:
    def __init__(self, text=None):
        self.text = text
        self.sent = []

    async def reply_text(self, text, reply_markup=None):
        self.sent.append((text, reply_markup))


class DummyCallbackQuery:
    def __init__(self):
        self.edited = []
        self.answered = 0

    async def answer(self):
        self.answered += 1

    async def edit_message_text(self, text, reply_markup=None):
        self.edited.append((text, reply_markup))


class DummyUser:
    def __init__(self, user_id):
        self.id = user_id


class DummyUpdate:
    def __init__(self, user_id, text=None, callback=False):
        self.effective_user = DummyUser(user_id)
        self.message = DummyMessage(text) if text is not None else None
        self.callback_query = DummyCallbackQuery() if callback else None


class DummyApp:
    def __init__(self, bot_data):
        self.bot_data = bot_data


class DummyContext:
    def __init__(self, bot_data):
        self.application = DummyApp(bot_data)


class DummyGenerator:
    async def generate(self, word, *, meaning_hint=None):
        return Generation(word=word, definition="d", example="e")


@pytest.mark.asyncio
async def test_regen_limit_reached(tmp_path):
    conn = connect(str(tmp_path / "t.sqlite"))
    init_db(conn)
    pending_repo = PendingRepository(conn)

    gen = Generation(word="run", definition="d", example="e")
    pending_repo.upsert(1, gen, regen_count=3, meaning_hint=None)

    update = DummyUpdate(user_id=1, callback=True)
    context = DummyContext(
        {
            "pending_repo": pending_repo,
            "example_generator": DummyGenerator(),
            "settings": type("S", (), {"max_regenerations": 3})(),
        }
    )

    from llmanki.bot.conversations import on_regenerate

    state = await on_regenerate(update, context)

    assert state == State.AWAIT_APPROVAL
    assert update.callback_query.edited


@pytest.mark.asyncio
async def test_no_pending_on_approve(tmp_path):
    conn = connect(str(tmp_path / "t.sqlite"))
    init_db(conn)
    user_repo = UserRepository(conn)
    pending_repo = PendingRepository(conn)
    user_repo.set_deck(1, "MyDeck")

    update = DummyUpdate(user_id=1, callback=True)
    context = DummyContext(
        {
            "user_repo": user_repo,
            "pending_repo": pending_repo,
            "deck_manager": type("DM", (), {})(),
        }
    )

    from llmanki.bot.conversations import on_approve

    state = await on_approve(update, context)

    assert state == State.AWAIT_WORD
    assert update.callback_query.edited
