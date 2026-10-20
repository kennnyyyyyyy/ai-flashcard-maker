import pytest

from flashcards.reader import UnsupportedFileError, read_document, split_into_chunks


def test_reads_a_text_file(tmp_path):
    notes = tmp_path / "notes.txt"
    notes.write_text("  PID stands for proportional, integral, derivative.  \n", encoding="utf-8")
    assert read_document(notes) == "PID stands for proportional, integral, derivative."


def test_reads_a_markdown_file(tmp_path):
    notes = tmp_path / "notes.md"
    notes.write_text("# Sensors\n\nLidar measures distance with light.", encoding="utf-8")
    assert "Lidar" in read_document(notes)


def test_rejects_unsupported_files(tmp_path):
    with pytest.raises(UnsupportedFileError, match=".docx"):
        read_document(tmp_path / "notes.docx")


def test_short_text_stays_in_one_chunk():
    assert split_into_chunks("One.\n\nTwo.") == ["One.\n\nTwo."]


def test_long_text_splits_between_paragraphs():
    text = "\n\n".join(["a" * 40, "b" * 40, "c" * 40])
    chunks = split_into_chunks(text, max_chars=90)
    assert chunks == ["a" * 40 + "\n\n" + "b" * 40, "c" * 40]


def test_empty_paragraphs_are_ignored():
    assert split_into_chunks("\n\n\n\nOnly this.\n\n   \n\n") == ["Only this."]
