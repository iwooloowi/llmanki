from __future__ import annotations

from typing import Optional

from llmanki.domain.models import Generation
from llmanki.services.llm_client import LLMClient


class ExampleGenerator:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def generate(self, word: str, *, meaning_hint: Optional[str] = None) -> Generation:
        data = await self._llm.generate_definition_and_example(word, meaning_hint=meaning_hint)
        definition = str(data.get("definition", "")).strip()
        example = str(data.get("example", "")).strip()

        if not definition or not example:
            # Fallback to a safer prompt for missing fields.
            data = await self._llm.generate_definition_and_example(
                word,
                meaning_hint=meaning_hint or "Provide a clear, common meaning.",
            )
            definition = str(data.get("definition", "")).strip()
            example = str(data.get("example", "")).strip()

        if not definition:
            definition = "(no definition returned)"
        if not example:
            example = f"{word}"

        return Generation(word=word, definition=definition, example=example)
