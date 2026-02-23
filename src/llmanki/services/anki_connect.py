from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import httpx


class AnkiConnectError(RuntimeError):
    pass


class AnkiConnectClient:
    def __init__(
        self,
        base_url: str,
        *,
        transport: Optional[httpx.AsyncBaseTransport] = None,
        max_retries: int = 2,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._transport = transport
        self._max_retries = max_retries

    async def _request(self, action: str, params: Dict[str, Any] | None = None) -> Any:
        payload = {"action": action, "version": 6, "params": params or {}}
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0, transport=self._transport) as client:
                    r = await client.post(self._base_url, json=payload)
                r.raise_for_status()
                data = r.json()
            except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    continue
                raise AnkiConnectError(
                    "AnkiConnect is not reachable. Make sure Anki is running with AnkiConnect installed."
                ) from exc

            if data.get("error"):
                raise AnkiConnectError(data["error"])
            return data.get("result")

        if last_exc:
            raise AnkiConnectError(
                "AnkiConnect is not reachable. Make sure Anki is running with AnkiConnect installed."
            ) from last_exc
        raise AnkiConnectError("Unknown AnkiConnect error")

    async def deck_exists(self, deck_name: str) -> bool:
        names = await self._request("deckNames")
        return deck_name in names

    async def version(self) -> int:
        return int(await self._request("version"))

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
