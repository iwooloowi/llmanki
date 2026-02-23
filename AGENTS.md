# Repository Guidelines

## Project Structure & Module Organization
- `src/llmanki/`: application code.
  - `bot/`: Telegram bot app, handlers, conversations, keyboards, and messages.
  - `services/`: LLM client, example generation, AnkiConnect client, deck manager.
  - `domain/`: core models and card building utilities.
  - `storage/`: SQLite schema and repositories.
  - `workflows/`: orchestration helpers (e.g., preview formatting).
  - `utils/`: rate limiting and shared helpers.
- `tests/`: pytest suite (unit + bot flow tests).
- `scripts/`: runnable entrypoints (e.g., `scripts/run_bot.py`).
- `.env.example`: required environment variables.

## Build, Test, and Development Commands
This project uses `uv`.
- `uv venv`: create the virtual environment.
- `uv sync --dev`: install dependencies (including dev tools).
- `uv run python scripts/run_bot.py`: run the Telegram bot locally.
- `uv run pytest`: run all tests.

## Coding Style & Naming Conventions
- Python 3.11+.
- Indentation: 4 spaces.
- Keep modules small and cohesive; place orchestration in `workflows/`.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes.
- Linting/formatting: `ruff` (configured in `pyproject.toml`).

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` for async tests.
- Naming: tests in `tests/` using `test_*.py` and `test_*` functions.
- Prefer unit tests with minimal doubles (see `tests/test_bot_flow.py`).
- Run locally with `uv run pytest`.

## Development Guideline
- Before writing code, create a test to cover your desired behaviour/feature/bugfix.
- New tests should fail after creating.
- Follow DRY priciples.
- Consider task is done when all related tests pass.
- Run `uvx pre-commit run --all-files` at the end of the task.

## Commit & Pull Request Guidelines
- No commit convention is defined in this repository (no Git history detected).
- Use short, imperative messages (e.g., “Add AnkiConnect tests”).
- For PRs, include: summary, linked issue (if any), and test results.

## Security & Configuration Tips
- Keep API keys in `.env` only; never commit secrets.
- AnkiConnect assumes local Anki at `http://127.0.0.1:8765`.
