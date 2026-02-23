from __future__ import annotations

import time
from dataclasses import dataclass

from llmanki.storage.repositories import UserState


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    allowed: bool
    reason: str | None
    daily_count: int
    last_request_ts: int
    retry_after: int | None


def _day_key(ts: int) -> int:
    return int(ts // 86400)


def check_and_update(
    user: UserState,
    *,
    daily_quota: int,
    cooldown_seconds: int,
    now_ts: int | None = None,
) -> RateLimitResult:
    now = now_ts or int(time.time())

    # reset daily count if day changed
    if _day_key(now) != _day_key(user.last_request_ts):
        daily_count = 0
    else:
        daily_count = user.daily_count

    if cooldown_seconds > 0 and user.last_request_ts > 0:
        elapsed = now - user.last_request_ts
        if elapsed < cooldown_seconds:
            return RateLimitResult(
                allowed=False,
                reason="cooldown",
                daily_count=daily_count,
                last_request_ts=user.last_request_ts,
                retry_after=cooldown_seconds - elapsed,
            )

    if daily_quota > 0 and daily_count >= daily_quota:
        return RateLimitResult(
            allowed=False,
            reason="quota",
            daily_count=daily_count,
            last_request_ts=user.last_request_ts,
            retry_after=None,
        )

    daily_count += 1
    return RateLimitResult(
        allowed=True,
        reason=None,
        daily_count=daily_count,
        last_request_ts=now,
        retry_after=None,
    )
