from llmanki.workflows.create_cards import format_preview
from llmanki.domain.models import Generation


def test_format_preview_includes_definition_and_example_in_one_message():
    gen = Generation(
        word="casa",
        definition="a house or home",
        example="La casa es grande.",
    )

    msg = format_preview(gen)

    assert isinstance(msg, str)
    assert "definition" in msg.lower()
    assert "example" in msg.lower()
    assert gen.definition in msg
    assert gen.example in msg
