# Roadmap

This roadmap targets a stable, shippable Telegram bot with reliable LLM card generation and Anki sync.

## 1) Define Done + Scope
- List the exact user flows to support (e.g., add word -> preview -> confirm -> sync; regenerate; deck selection; error recovery).
- Identify non-goals (e.g., advanced scheduling, multi-deck per user, multi-language).

## 2) Stabilize Core Workflows
- Review bot conversations in `src/llmanki/bot/` for end-to-end flow completeness.
- Ensure deck selection caching and fallback behavior is consistent.
- Lock down rate limiting and quota enforcement paths (cooldown, daily cap, regen cap).

## 3) LLM + AnkiConnect Reliability
- Validate LLM prompt/output contracts; add strict parsing and fallback messages for malformed output.
- Add AnkiConnect failure handling with retries and actionable user feedback.
- Ensure idempotency when creating cards to avoid duplicates on retries.

## 4) Persistence and Data Integrity
- Confirm SQLite schema covers user state (deck, quota counters, last action timestamps).
- Add migrations/upgrade path if schema might evolve.
- Add basic data cleanup (expired quotas, old pending items).

## 5) Testing
- Unit tests for services (LLM client, card builder, AnkiConnect client).
- Bot flow tests for main conversation paths (success, regen limit, quota exceeded, Anki down).
- Run `uv run pytest` and fix failures.

## 6) Configuration and Observability
- Validate `.env.example` is complete and minimal.
- Add structured logging around user actions and external calls.
- Add startup checks (LLM credentials present, AnkiConnect reachable).

## 7) Operational Readiness
- Write a short runbook (setup, common errors, reset quota, troubleshooting AnkiConnect).
- Confirm non-interactive startup behavior (`scripts/run_bot.py`).

## 8) Polish
- Improve user-facing messages (clear, short, actionable).
- Add a minimal `/help` and `/status` command if missing.
- Recheck rate limit UX (clear remaining quota messaging).
