import csv

from flashcards.exporter import to_markdown, write_csv, write_markdown
from flashcards.generator import Flashcard

CARDS = [
    Flashcard("What does PID stand for?", "Proportional, integral, derivative."),
    Flashcard("What does a lidar measure?", "Distance, using laser light."),
]


def test_csv_has_one_row_per_card(tmp_path):
    path = tmp_path / "cards.csv"
    write_csv(CARDS, path)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows == [[c.question, c.answer] for c in CARDS]


def test_csv_keeps_commas_inside_answers(tmp_path):
    path = tmp_path / "cards.csv"
    write_csv(CARDS[:1], path)
    with open(path, newline="", encoding="utf-8") as f:
        assert next(csv.reader(f))[1] == "Proportional, integral, derivative."


def test_markdown_numbers_the_cards():
    text = to_markdown(CARDS, "Robotics")
    assert text.startswith("# Robotics")
    assert "**2. What does a lidar measure?**" in text


def test_write_markdown_creates_the_file(tmp_path):
    path = tmp_path / "cards.md"
    write_markdown(CARDS, path)
    assert "Distance, using laser light." in path.read_text(encoding="utf-8")
