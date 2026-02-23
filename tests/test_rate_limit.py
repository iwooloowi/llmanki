from llmanki.storage.repositories import UserState
from llmanki.utils.rate_limit import check_and_update, get_rate_limit_status


def test_rate_limit_allows_within_quota_and_cooldown():
    user = UserState(user_id=1, deck_name=None, daily_count=0, last_request_ts=0)
    result = check_and_update(user, daily_quota=20, cooldown_seconds=10, now_ts=100)
    assert result.allowed is True
    assert result.daily_count == 1
    assert result.last_request_ts == 100


def test_rate_limit_blocks_cooldown():
    user = UserState(user_id=1, deck_name=None, daily_count=1, last_request_ts=100)
    result = check_and_update(user, daily_quota=20, cooldown_seconds=10, now_ts=105)
    assert result.allowed is False
    assert result.reason == "cooldown"
    assert result.retry_after == 5


def test_rate_limit_blocks_quota():
    user = UserState(user_id=1, deck_name=None, daily_count=20, last_request_ts=100)
    result = check_and_update(user, daily_quota=20, cooldown_seconds=0, now_ts=200)
    assert result.allowed is False
    assert result.reason == "quota"


def test_rate_limit_resets_daily_count_on_new_day():
    user = UserState(user_id=1, deck_name=None, daily_count=5, last_request_ts=100)
    # next day boundary crossed
    result = check_and_update(user, daily_quota=20, cooldown_seconds=0, now_ts=90000)
    assert result.allowed is True
    assert result.daily_count == 1


def test_rate_limit_status_reports_remaining_and_cooldown():
    user = UserState(user_id=1, deck_name=None, daily_count=5, last_request_ts=100)
    status = get_rate_limit_status(user, daily_quota=20, cooldown_seconds=10, now_ts=105)
    assert status.daily_remaining == 15
    assert status.cooldown_remaining == 5
