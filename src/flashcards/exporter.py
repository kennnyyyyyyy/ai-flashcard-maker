"""Saves flashcards as CSV (for importing into Anki or Quizlet) and Markdown."""

import csv
import io
from pathlib import Path


def to_csv(cards):
    """Two columns, question then answer, with no header row so Anki imports it directly."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    for card in cards:
        writer.writerow([card.question, card.answer])
    return out.getvalue()


def write_csv(cards, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(to_csv(cards))


def to_markdown(cards, title):
    lines = [f"# {title}", ""]
    for number, card in enumerate(cards, start=1):
        lines += [f"**{number}. {card.question}**", "", card.answer, ""]
    return "\n".join(lines)


def write_markdown(cards, path, title="Flashcards"):
    Path(path).write_text(to_markdown(cards, title), encoding="utf-8")
