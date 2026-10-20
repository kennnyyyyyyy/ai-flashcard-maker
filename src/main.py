"""Make flashcards from a document.

Usage:
    python src/main.py examples/sample-notes.txt
    python src/main.py lecture.pdf --max-cards 20 --out lecture-cards
"""

import argparse
import sys
from pathlib import Path

from flashcards.config import MissingApiKeyError, load_settings
from flashcards.exporter import write_csv, write_markdown
from flashcards.generator import generate_flashcards
from flashcards.reader import UnsupportedFileError, read_document


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Turn a document into flashcards with GPT-4o-mini.")
    parser.add_argument("document", help="a .txt, .md or .pdf file")
    parser.add_argument("--max-cards", type=int, default=10, help="most cards to make (default 10)")
    parser.add_argument("--out", help="output name without extension (default: next to the document)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        settings = load_settings()
        text = read_document(args.document)
    except (MissingApiKeyError, UnsupportedFileError, FileNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key)
    print(f"Reading {args.document} and asking {settings.model} for up to {args.max_cards} cards...")
    cards = generate_flashcards(client, settings.model, text, args.max_cards)

    document = Path(args.document)
    out = Path(args.out) if args.out else document.with_name(document.stem + "-flashcards")
    write_csv(cards, out.with_suffix(".csv"))
    write_markdown(cards, out.with_suffix(".md"), title=f"Flashcards: {document.name}")

    for number, card in enumerate(cards, start=1):
        print(f"\n{number}. {card.question}\n   {card.answer}")
    print(f"\nSaved {len(cards)} cards to {out.with_suffix('.csv')} and {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
