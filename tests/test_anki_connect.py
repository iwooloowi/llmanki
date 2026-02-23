import json
import httpx
import pytest

from llmanki.services.anki_connect import AnkiConnectClient, AnkiConnectError


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler):
        self._handler = handler

    async def handle_async_request(self, request):
        return self._handler(request)


def _json_response(payload, status=200):
    return httpx.Response(status, json=payload)


@pytest.mark.asyncio
async def test_request_retries_on_connection_error():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectError("boom", request=request)
        return _json_response({"result": ["MyDeck"], "error": None})

    transport = httpx.MockTransport(handler)
    client = AnkiConnectClient("http://localhost:8765", transport=transport, max_retries=1)

    assert await client.deck_exists("MyDeck") is True
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_request_wraps_connection_error():
    def handler(request):
        raise httpx.ConnectError("boom", request=request)

    transport = httpx.MockTransport(handler)
    client = AnkiConnectClient("http://localhost:8765", transport=transport, max_retries=0)

    with pytest.raises(AnkiConnectError) as excinfo:
        await client.deck_exists("MyDeck")

    assert "AnkiConnect" in str(excinfo.value)


@pytest.mark.asyncio
async def test_deck_exists_true():
    def handler(request):
        body = json.loads(request.content)
        assert body["action"] == "deckNames"
        return _json_response({"result": ["MyDeck"], "error": None})

    client = AnkiConnectClient("http://localhost:8765")
    client._base_url = "http://test"
    client._request = _make_request(handler)

    assert await client.deck_exists("MyDeck") is True


@pytest.mark.asyncio
async def test_version_request():
    def handler(request):
        body = json.loads(request.content)
        assert body["action"] == "version"
        return _json_response({"result": 6, "error": None})

    transport = httpx.MockTransport(handler)
    client = AnkiConnectClient("http://localhost:8765", transport=transport, max_retries=0)

    assert await client.version() == 6


@pytest.mark.asyncio
async def test_add_basic_cards_payload():
    captured = {}

    def handler(request):
        body = json.loads(request.content)
        captured["body"] = body
        return _json_response({"result": [1, 2], "error": None})

    client = AnkiConnectClient("http://localhost:8765")
    client._base_url = "http://test"
    client._request = _make_request(handler)

    result = await client.add_basic_cards(
        "MyDeck",
        [{"front": "F1", "back": "B1"}, {"front": "F2", "back": "B2"}],
    )

    assert result == [1, 2]
    notes = captured["body"]["params"]["notes"]
    assert notes[0]["deckName"] == "MyDeck"
    assert notes[0]["modelName"] == "Basic"
    assert notes[0]["fields"]["Front"] == "F1"
    assert notes[0]["fields"]["Back"] == "B1"


@pytest.mark.asyncio
async def test_request_raises_on_error():
    async def handler(request):
        return _json_response({"result": None, "error": "boom"})

    client = AnkiConnectClient("http://localhost:8765")
    client._base_url = "http://test"
    client._request = _make_request(handler)

    with pytest.raises(AnkiConnectError):
        await client._request("any")


# Helper to replace _request with a custom transport


def _make_request(handler):
    async def _request(action, params=None):
        payload = {"action": action, "version": 6, "params": params or {}}
        request = httpx.Request("POST", "http://test", json=payload)
        response = handler(request)
        if hasattr(response, "__await__"):
            response = await response
        data = response.json()
        if data.get("error"):
            raise AnkiConnectError(data["error"])
        return data.get("result")

    return _request
