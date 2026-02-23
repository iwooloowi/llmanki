from __future__ import annotations

import re
from typing import List

from llmanki.domain.models import Card, Generation


def mask_example(example: str, word: str) -> str:
    # Replace the word and common English inflections, case-insensitive.
    # This is a pragmatic default; can be extended per language later.
    escaped = re.escape(word)
    pattern = re.compile(rf"\b{escaped}(?:s|es|ed|ing)?\b", re.IGNORECASE)
    return pattern.sub("___", example)


def build_basic_cards(gen: Generation) -> List[Card]:
    definition_card = Card(front=gen.definition, back=gen.word)
    masked = mask_example(gen.example, gen.word)
    example_card = Card(front=masked, back=gen.example)
    return [definition_card, example_card]
