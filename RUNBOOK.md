# Runbook

## Setup
- Install dependencies with `uv venv` then `uv sync --dev`.
- Create `.env` from `.env.example` and set:
  - `TELEGRAM_BOT_TOKEN`
  - `OPENAI_API_KEY`
  - Optional: `OPENAI_MODEL`, `ANKI_CONNECT_URL`, `DB_PATH`
- Start Anki desktop and confirm AnkiConnect is installed and enabled.

## Run Locally
- `uv run python scripts/run_bot.py`
- The bot performs startup checks for required env vars and AnkiConnect reachability.

## Common Issues
- **AnkiConnect not reachable**: Make sure Anki is running and AnkiConnect is installed. Default URL is `http://127.0.0.1:8765`.
- **Missing env vars**: Ensure `TELEGRAM_BOT_TOKEN` and `OPENAI_API_KEY` are set in `.env`.
- **Bot not responding**: Verify the bot token is correct and the bot is not blocked on Telegram.

## Operational Checks
- Send `/start` to the bot and confirm it asks for a deck if none is set.
- Send a word and confirm you receive a preview with approve/regenerate options.
- Approve and confirm cards appear in Anki.

## Reset Daily Quota
- Delete or edit the SQLite DB at `DB_PATH` (default `./llmanki.sqlite`).
- Alternatively, reset the `daily_count` and `last_request_ts` values in the `users` table.
