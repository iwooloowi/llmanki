# llmanki

Telegram bot that generates Anki cards using LLMs and syncs via AnkiConnect.

## Requirements
- Python 3.11+
- Anki desktop with AnkiConnect installed and running

## Setup (uv)
1. Create and sync the environment:

```bash
uv venv
uv sync --dev
```

2. Configure environment:

```bash
cp .env.example .env
```

3. Run the bot:

```bash
uv run python scripts/run_bot.py
```

## Notes
- The bot asks the user once for a target deck, then reuses it.
- Daily quota: 20 words/user, cooldown: 10s, max regenerations: 3.
- Uses `gpt-4.1-mini` by default.
