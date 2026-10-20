"""Reads text out of .txt, .md, .pdf and .docx files and splits it into chunks.

Long documents are split into chunks so each request to the model stays a
sensible size. Chunks break between paragraphs, never mid-sentence.
"""

from pathlib import Path

SUPPORTED = {".txt", ".md", ".pdf", ".docx"}


class UnsupportedFileError(ValueError):
    pass


def read_document(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise UnsupportedFileError(
            f"Can't read {suffix or 'files without an extension'}. Use one of: {', '.join(sorted(SUPPORTED))}"
        )
    if suffix == ".pdf":
        from pypdf import PdfReader

        pages = [page.extract_text() or "" for page in PdfReader(path).pages]
        return "\n\n".join(pages).strip()
    if suffix == ".docx":
        from docx import Document

        paragraphs = [p.text.strip() for p in Document(path).paragraphs]
        return "\n\n".join(p for p in paragraphs if p).strip()
    return path.read_text(encoding="utf-8").strip()


def split_into_chunks(text, max_chars=6000):
    """Group paragraphs into chunks of at most max_chars characters.

    A single paragraph longer than max_chars becomes its own chunk.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + 2 + len(paragraph) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        chunks.append(current)
    return chunks
