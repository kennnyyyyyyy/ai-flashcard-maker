"""Saves flashcards as CSV (for importing into Anki or Quizlet) and Markdown."""

import csv
from pathlib import Path


def write_csv(cards, path):
    """Two columns, question then answer, with no header row so Anki imports it directly."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for card in cards:
            writer.writerow([card.question, card.answer])


def to_markdown(cards, title):
    lines = [f"# {title}", ""]
    for number, card in enumerate(cards, start=1):
        lines += [f"**{number}. {card.question}**", "", card.answer, ""]
    return "\n".join(lines)


def write_markdown(cards, path, title="Flashcards"):
    Path(path).write_text(to_markdown(cards, title), encoding="utf-8")
