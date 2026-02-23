from __future__ import annotations


def welcome() -> str:
    return (
        "Send me a word and I will generate a definition and example, then create Anki cards.\n"
        "First, please tell me which Anki deck to use."
    )


def ask_deck() -> str:
    return "Which Anki deck should I use?"


def deck_set(deck_name: str) -> str:
    return f"Deck set to: {deck_name}. Send a word."


def deck_not_found(deck_name: str) -> str:
    return f"Deck not found: {deck_name}. Please create it in Anki and try again."


def generating() -> str:
    return "Generating definition and example..."


def preview_header() -> str:
    return "Here is the generated content:"


def approved() -> str:
    return "Cards added to Anki and synced."


def cancelled() -> str:
    return "Cancelled. Send another word."


def regen_limit_reached() -> str:
    return "Regeneration limit reached for this word."


def no_pending() -> str:
    return "No pending generation. Send a word first."


def quota_exceeded() -> str:
    return "Daily quota reached. Try again tomorrow."


def cooldown(wait_seconds: int) -> str:
    return f"Please wait {wait_seconds}s before the next request."
