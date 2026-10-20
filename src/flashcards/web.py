"""A small web page for the flashcard maker.

    python src/web.py        then open http://127.0.0.1:5000

Paste text or upload a .pdf, .docx, .txt or .md file. The page shows the cards
and lets you download them as CSV or Markdown. The API key never leaves the
server: it is read from .env, the same way as the command-line tool.
"""

import io
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from flashcards.config import MissingApiKeyError, load_settings
from flashcards.exporter import to_csv, to_markdown
from flashcards.generator import Flashcard, generate_flashcards
from flashcards.reader import SUPPORTED, UnsupportedFileError, read_document

MAX_UPLOAD_MB = 15
MIN_CARDS, MAX_CARDS, DEFAULT_CARDS = 3, 30, 10


def error(message, status=400):
    return jsonify(error=message), status


def card_count(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return DEFAULT_CARDS
    return max(MIN_CARDS, min(MAX_CARDS, number))


def read_upload(upload):
    """Save the upload to a temporary file so the normal reader can open it."""
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise UnsupportedFileError(
            f"Can't read {suffix or 'files without an extension'}. Use a PDF, Word (.docx), .txt or .md file."
        )
    handle, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(handle, "wb") as f:
            upload.save(f)
        return read_document(path)
    finally:
        os.remove(path)


def create_app(make_client=None, dotenv_path=".env"):
    """make_client(settings) builds the OpenAI client; tests pass a fake one."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

    def client_and_model():
        settings = load_settings(dotenv_path)
        if make_client is not None:
            return make_client(settings), settings.model
        from openai import OpenAI

        return OpenAI(api_key=settings.api_key), settings.model

    @app.get("/")
    def index():
        return render_template("index.html", accept=",".join(sorted(SUPPORTED)), min_cards=MIN_CARDS,
                               max_cards=MAX_CARDS, default_cards=DEFAULT_CARDS, max_mb=MAX_UPLOAD_MB)

    @app.post("/api/cards")
    def make_cards():
        count = card_count(request.form.get("count"))
        upload = request.files.get("file")
        try:
            if upload and upload.filename:
                text, source = read_upload(upload), upload.filename
            else:
                text, source = request.form.get("text", "").strip(), "your notes"
        except UnsupportedFileError as e:
            return error(str(e))
        except Exception:
            return error("That file couldn't be read. Check that it opens on your computer and try again.")
        if not text:
            return error("There's no text to work with. Paste some notes or choose a file with text in it.")
        try:
            client, model = client_and_model()
        except MissingApiKeyError as e:
            return error(str(e), 500)
        try:
            cards = generate_flashcards(client, model, text, count)
        except Exception as e:
            return error(f"The request to {model} didn't work: {e}", 502)
        if not cards:
            return error("No flashcards came back. Try a longer piece of text.", 422)
        return jsonify(source=source, model=model, cards=[asdict(c) for c in cards])

    @app.post("/api/export/<fmt>")
    def export(fmt):
        data = request.get_json(silent=True) or {}
        cards = [Flashcard(str(c.get("question", "")).strip(), str(c.get("answer", "")).strip())
                 for c in data.get("cards", []) if isinstance(c, dict)]
        cards = [c for c in cards if c.question and c.answer]
        if not cards:
            return error("There are no cards to download yet.")
        stem = Path(str(data.get("name") or "flashcards")).stem or "flashcards"
        if fmt == "csv":
            body, mimetype, ext = to_csv(cards), "text/csv", "csv"
        elif fmt == "md":
            body, mimetype, ext = to_markdown(cards, f"Flashcards: {data.get('name') or 'my notes'}"), "text/markdown", "md"
        else:
            return error("Unknown format. Use csv or md.", 404)
        return send_file(io.BytesIO(body.encode("utf-8")), mimetype=mimetype, as_attachment=True,
                         download_name=f"{stem}-flashcards.{ext}")

    @app.errorhandler(413)
    def too_big(_):
        return error(f"That file is too big. The limit is {MAX_UPLOAD_MB} MB.", 413)

    return app
