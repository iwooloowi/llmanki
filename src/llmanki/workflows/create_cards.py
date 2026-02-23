from __future__ import annotations

from llmanki.domain.models import Generation


def format_preview(gen: Generation) -> str:
    return f"Definition:\n{gen.definition}\n\nExample:\n{gen.example}"
