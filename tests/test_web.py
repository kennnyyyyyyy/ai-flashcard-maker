import io
import json
from types import SimpleNamespace

import pytest

from flashcards.web import create_app


class FakeClient:
    """Stands in for the OpenAI client so the web tests never call the real API."""

    def __init__(self, cards):
        self.cards = cards
        self.prompts = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.prompts.append(kwargs["messages"][-1]["content"])
        content = json.dumps({"cards": [{"question": q, "answer": a} for q, a in self.cards]})
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


@pytest.fixture
def fake():
    return FakeClient([("What does a servo do?", "Turns to a set angle."), ("What is odometry?", "Estimating distance from wheel turns.")])


@pytest.fixture
def client(tmp_path, fake):
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=sk-test\n", encoding="utf-8")
    app = create_app(make_client=lambda settings: fake, dotenv_path=env)
    return app.test_client()


def test_home_page_loads(client):
    page = client.get("/")
    assert page.status_code == 200
    assert b"Turn your notes into" in page.data
    assert b".docx" in page.data


def test_makes_cards_from_pasted_text(client, fake):
    res = client.post("/api/cards", data={"text": "Servos turn to a set angle.", "count": "5"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["source"] == "your notes"
    assert body["cards"][0] == {"question": "What does a servo do?", "answer": "Turns to a set angle."}
    assert "Servos turn to a set angle." in fake.prompts[0]


def test_makes_cards_from_a_word_file(client, fake):
    from docx import Document

    doc = Document()
    doc.add_paragraph("Odometry estimates distance from wheel encoder ticks.")
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    res = client.post("/api/cards", data={"file": (buffer, "lecture.docx"), "count": "5"},
                      content_type="multipart/form-data")
    assert res.status_code == 200
    assert res.get_json()["source"] == "lecture.docx"
    assert "wheel encoder ticks" in fake.prompts[0]


def test_rejects_unsupported_files(client):
    res = client.post("/api/cards", data={"file": (io.BytesIO(b"x"), "slides.pptx")},
                      content_type="multipart/form-data")
    assert res.status_code == 400
    assert ".pptx" in res.get_json()["error"]


def test_empty_text_gives_a_friendly_error(client):
    res = client.post("/api/cards", data={"text": "   "})
    assert res.status_code == 400
    assert "no text" in res.get_json()["error"]


def test_missing_api_key_is_reported(tmp_path, fake):
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    app = create_app(make_client=lambda settings: fake, dotenv_path=env)
    res = app.test_client().post("/api/cards", data={"text": "Some notes."})
    assert res.status_code == 500
    assert "OPENAI_API_KEY" in res.get_json()["error"]


def test_card_count_is_kept_in_range(client, fake):
    client.post("/api/cards", data={"text": "Notes.", "count": "500"})
    assert "up to 30 flashcards" in fake.prompts[0]


def test_downloads_csv_and_markdown(client):
    cards = [{"question": "What is PID?", "answer": "A feedback controller."}]
    csv_res = client.post("/api/export/csv", json={"cards": cards, "name": "lecture.docx"})
    assert csv_res.status_code == 200
    assert "lecture-flashcards.csv" in csv_res.headers["Content-Disposition"]
    assert csv_res.data.decode() == "What is PID?,A feedback controller.\n"
    md_res = client.post("/api/export/md", json={"cards": cards, "name": "lecture.docx"})
    assert b"**1. What is PID?**" in md_res.data


def test_download_needs_cards(client):
    assert client.post("/api/export/csv", json={"cards": []}).status_code == 400
