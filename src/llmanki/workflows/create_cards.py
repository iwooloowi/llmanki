from __future__ import annotations

from llmanki.domain.models import Generation


def format_preview(gen: Generation) -> str:
    return (
        "Definition:\n"
        f"{gen.definition}\n\n"
        "Example:\n"
        f"{gen.example}"
    )
