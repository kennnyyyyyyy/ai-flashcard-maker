"""Asks the OpenAI model to condense text into question-and-answer flashcards."""

import json
from dataclasses import dataclass

from flashcards.reader import split_into_chunks

SYSTEM_PROMPT = """You turn study material into flashcards.
Reply with JSON only, in this shape: {"cards": [{"question": "...", "answer": "..."}]}
Rules:
- One fact or idea per card.
- Only use information that is in the text.
- Keep each answer under 25 words.
- Skip trivia; pick what a student would be tested on."""


@dataclass
class Flashcard:
    question: str
    answer: str


def parse_cards(raw):
    """Turn the model's JSON reply into Flashcards, skipping incomplete ones."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"The model did not return valid JSON: {error}") from error
    cards = []
    for item in data.get("cards", []):
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if question and answer:
            cards.append(Flashcard(question, answer))
    return cards


def request_cards(client, model, text, count):
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Make up to {count} flashcards from this text:\n\n{text}"},
        ],
    )
    return parse_cards(response.choices[0].message.content)


def generate_flashcards(client, model, text, max_cards=10):
    """Split the text into chunks, ask for cards from each, and drop duplicates."""
    chunks = split_into_chunks(text)
    if not chunks:
        return []
    per_chunk = max(1, -(-max_cards // len(chunks)))  # round up
    cards = []
    seen = set()
    for chunk in chunks:
        for card in request_cards(client, model, chunk, per_chunk):
            key = card.question.lower()
            if key not in seen:
                seen.add(key)
                cards.append(card)
    return cards[:max_cards]
