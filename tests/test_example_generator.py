import pytest

from llmanki.services.example_generator import ExampleGenerator


class DummyLLM:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    async def generate_definition_and_example(self, word, *, meaning_hint=None):
        self.calls.append((word, meaning_hint))
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_generator_fallback_when_missing_fields():
    responses = [
        {"definition": "", "example": ""},
        {"definition": "d", "example": "e"},
    ]
    gen = ExampleGenerator(DummyLLM(responses))

    result = await gen.generate("run")

    assert result.definition == "d"
    assert result.example == "e"


@pytest.mark.asyncio
async def test_generator_sets_placeholder_when_still_missing():
    responses = [
        {"definition": "", "example": ""},
        {"definition": "", "example": ""},
    ]
    gen = ExampleGenerator(DummyLLM(responses))

    result = await gen.generate("run")

    assert result.definition == "(no definition returned)"
    assert result.example == "run"


@pytest.mark.asyncio
async def test_generator_handles_non_dict_response():
    responses = [
        "not-a-dict",
        {"definition": "d", "example": "e"},
    ]
    gen = ExampleGenerator(DummyLLM(responses))

    result = await gen.generate("run")

    assert result.definition == "d"
    assert result.example == "e"
