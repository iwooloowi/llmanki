from __future__ import annotations

import json
from typing import Any, Dict, List

import httpx


class AnkiConnectError(RuntimeError):
    pass


class AnkiConnectClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def _request(self, action: str, params: Dict[str, Any] | None = None) -> Any:
        payload = {"action": action, "version": 6, "params": params or {}}
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(self._base_url, json=payload)
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise AnkiConnectError(data["error"])
        return data.get("result")

    async def deck_exists(self, deck_name: str) -> bool:
        names = await self._request("deckNames")
        return deck_name in names

    async def add_basic_cards(
        self,
        deck_name: str,
        cards: List[Dict[str, str]],
    ) -> List[int]:
        notes = []
        for c in cards:
            notes.append(
                {
                    "deckName": deck_name,
                    "modelName": "Basic",
                    "fields": {"Front": c["front"], "Back": c["back"]},
                    "options": {"allowDuplicate": False},
                }
            )

        return await self._request("addNotes", {"notes": notes})

    async def sync(self) -> None:
        await self._request("sync")
