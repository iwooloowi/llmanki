from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Generation:
    word: str
    definition: str
    example: str


@dataclass(frozen=True, slots=True)
class Card:
    front: str
    back: str
