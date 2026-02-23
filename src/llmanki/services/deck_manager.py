from __future__ import annotations

from typing import Iterable, List

from llmanki.domain.models import Card
from llmanki.services.anki_connect import AnkiConnectClient


class DeckManager:
    def __init__(self, anki: AnkiConnectClient) -> None:
        self._anki = anki

    async def ensure_deck(self, deck_name: str) -> bool:
        return await self._anki.deck_exists(deck_name)

    async def add_cards(self, deck_name: str, cards: Iterable[Card]) -> List[int]:
        payload = [{"front": c.front, "back": c.back} for c in cards]
        return await self._anki.add_basic_cards(deck_name, payload)

    async def sync(self) -> None:
        await self._anki.sync()
