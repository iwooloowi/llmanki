from llmanki.domain.models import Generation
from llmanki.storage.db import connect, init_db
from llmanki.storage.repositories import PendingRepository, UserRepository


def test_user_repository_creates_default_user(tmp_path):
    conn = connect(str(tmp_path / "test.sqlite"))
    init_db(conn)

    users = UserRepository(conn)
    state = users.get(123)

    assert state.user_id == 123
    assert state.deck_name is None
    assert state.daily_count == 0
    assert state.last_request_ts == 0


def test_pending_repository_upsert_and_get(tmp_path):
    conn = connect(str(tmp_path / "test.sqlite"))
    init_db(conn)

    pending = PendingRepository(conn)
    gen = Generation(word="run", definition="to move fast", example="I run daily.")

    pending.upsert(user_id=1, generation=gen, regen_count=2, meaning_hint=None)

    result = pending.get(1)
    assert result is not None
    assert result.generation.word == "run"
    assert result.regen_count == 2
