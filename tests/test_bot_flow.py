import pytest
from telegram import InlineKeyboardMarkup

from llmanki.bot.conversations import State
from llmanki.storage.repositories import PendingRepository, UserRepository
from llmanki.storage.db import connect, init_db
from llmanki.domain.models import Generation


class DummyMessage:
    def __init__(self, text):
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


class DummyDeckManager:
    def __init__(self, exists=True):
        self._exists = exists
        self.added = []
        self.synced = 0

    async def ensure_deck(self, name):
        return self._exists

    async def add_cards(self, deck_name, cards):
        self.added.append((deck_name, list(cards)))
        return [1, 2]

    async def sync(self):
        self.synced += 1


class DummyGenerator:
    def __init__(self, gen):
        self._gen = gen
        self.calls = []

    async def generate(self, word, *, meaning_hint=None):
        self.calls.append((word, meaning_hint))
        return self._gen


@pytest.mark.asyncio
async def test_on_deck_sets_deck_and_moves_to_await_word(tmp_path):
    conn = connect(str(tmp_path / "t.sqlite"))
    init_db(conn)
    user_repo = UserRepository(conn)

    update = DummyUpdate(user_id=1, text="MyDeck")
    context = DummyContext(
        {
            "user_repo": user_repo,
            "deck_manager": DummyDeckManager(exists=True),
        }
    )

    from llmanki.bot.conversations import on_deck

    state = await on_deck(update, context)

    assert state == State.AWAIT_WORD
    assert user_repo.get(1).deck_name == "MyDeck"


@pytest.mark.asyncio
async def test_on_word_generates_preview_and_sets_pending(tmp_path):
    conn = connect(str(tmp_path / "t.sqlite"))
    init_db(conn)
    user_repo = UserRepository(conn)
    pending_repo = PendingRepository(conn)
    user_repo.set_deck(1, "MyDeck")

    gen = Generation(word="run", definition="to move", example="I run daily.")
    update = DummyUpdate(user_id=1, text="run")
    context = DummyContext(
        {
            "user_repo": user_repo,
            "pending_repo": pending_repo,
            "example_generator": DummyGenerator(gen),
            "settings": type("S", (), {"daily_quota": 20, "cooldown_seconds": 10, "max_regenerations": 3})(),
        }
    )

    from llmanki.bot.conversations import on_word

    state = await on_word(update, context)

    assert state == State.AWAIT_APPROVAL
    pending = pending_repo.get(1)
    assert pending is not None
    assert pending.generation.word == "run"

    # preview message includes a keyboard
    assert update.message.sent
    _, markup = update.message.sent[-1]
    assert isinstance(markup, InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_on_approve_adds_cards_and_clears_pending(tmp_path):
    conn = connect(str(tmp_path / "t.sqlite"))
    init_db(conn)
    user_repo = UserRepository(conn)
    pending_repo = PendingRepository(conn)
    user_repo.set_deck(1, "MyDeck")

    gen = Generation(word="play", definition="to engage", example="Kids play.")
    pending_repo.upsert(1, gen, regen_count=0, meaning_hint=None)

    update = DummyUpdate(user_id=1, callback=True)
    context = DummyContext(
        {
            "user_repo": user_repo,
            "pending_repo": pending_repo,
            "deck_manager": DummyDeckManager(exists=True),
        }
    )

    from llmanki.bot.conversations import on_approve

    state = await on_approve(update, context)

    assert state == State.AWAIT_WORD
    assert pending_repo.get(1) is None
    assert update.callback_query.answered == 1
    assert update.callback_query.edited
