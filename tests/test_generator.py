import json
from types import SimpleNamespace

import pytest

from flashcards.generator import Flashcard, generate_flashcards, parse_cards


class FakeClient:
    """Stands in for the OpenAI client so tests never call the real API."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append(kwargs)
        content = self.replies.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def reply(*pairs):
    return json.dumps({"cards": [{"question": q, "answer": a} for q, a in pairs]})


def test_parse_cards_reads_question_and_answer():
    cards = parse_cards(reply(("What is PID?", "A feedback controller.")))
    assert cards == [Flashcard("What is PID?", "A feedback controller.")]


def test_parse_cards_skips_incomplete_cards():
    raw = json.dumps({"cards": [{"question": "Q?", "answer": ""}, {"question": "Q2?", "answer": "A2"}]})
    assert parse_cards(raw) == [Flashcard("Q2?", "A2")]


def test_parse_cards_rejects_invalid_json():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_cards("not json")


def test_generate_sends_the_model_and_text():
    client = FakeClient([reply(("Q?", "A"))])
    generate_flashcards(client, "gpt-4o-mini", "Some notes.")
    request = client.requests[0]
    assert request["model"] == "gpt-4o-mini"
    assert "Some notes." in request["messages"][1]["content"]
    assert request["response_format"] == {"type": "json_object"}


def test_generate_removes_duplicate_questions_across_chunks():
    long_text = ("a" * 5000) + "\n\n" + ("b" * 5000)  # two chunks
    client = FakeClient([reply(("Same question?", "A")), reply(("same question?", "B"), ("New?", "C"))])
    cards = generate_flashcards(client, "gpt-4o-mini", long_text)
    assert [c.question for c in cards] == ["Same question?", "New?"]


def test_generate_respects_max_cards():
    client = FakeClient([reply(*[(f"Q{i}?", "A") for i in range(8)])])
    assert len(generate_flashcards(client, "gpt-4o-mini", "Notes.", max_cards=5)) == 5


def test_empty_text_makes_no_api_call():
    client = FakeClient([])
    assert generate_flashcards(client, "gpt-4o-mini", "   ") == []
    assert client.requests == []
