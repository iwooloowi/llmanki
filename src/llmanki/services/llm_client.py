from __future__ import annotations

import json
from typing import Any, Dict, Optional

from openai import AsyncOpenAI


class LLMClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required")
        if not model:
            raise ValueError("OPENAI_MODEL is required")

        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self._model = model

    async def generate_definition_and_example(
        self,
        word: str,
        *,
        meaning_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        system = (
            "You are a lexicographer and language tutor. "
            "Return only JSON with keys: definition, example. "
            "Definition should be concise. Example should be a single sentence if possible."
        )

        if meaning_hint:
            user = (
                f"Word: {word}\n"
                f"Use this meaning: {meaning_hint}\n"
                "Return the definition and an example sentence for that meaning."
            )
        else:
            user = (
                f"Word: {word}\n"
                "If multiple meanings exist, choose the most common meaning. "
                "Return the definition and an example sentence for that meaning."
            )

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.6,
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content or "{}"
        return json.loads(content)
