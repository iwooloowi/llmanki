import pytest

from llmanki.domain.card_builder import build_basic_cards, mask_example
from llmanki.domain.models import Card, Generation


def test_mask_example_replaces_word_and_variations():
    word = "play"
    example = "I played and play, playing. PLAY!"  # includes variations and casing
    masked = mask_example(example, word)
    assert masked == "I ___ and ___, ___. ___!"


def test_build_basic_cards_creates_two_cards_with_expected_sides():
    gen = Generation(
        word="play",
        definition="to engage in activity for enjoyment",
        example="Kids play in the park.",
    )

    cards = build_basic_cards(gen)

    assert isinstance(cards, list)
    assert len(cards) == 2
    assert all(isinstance(c, Card) for c in cards)

    # Card 1: definition front, word back
    assert cards[0].front == gen.definition
    assert cards[0].back == gen.word

    # Card 2: masked example front, full example back
    assert cards[1].front == "Kids ___ in the park."
    assert cards[1].back == gen.example
