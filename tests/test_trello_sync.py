import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "trello_sync.py"
spec = importlib.util.spec_from_file_location("trello_sync", SCRIPT)
trello_sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trello_sync)


def test_finds_card_links_in_a_pr_description():
    body = "Closes #2\n\nTrello card: https://trello.com/c/AbCd1234/5-document-reader"
    assert trello_sync.card_ids(body) == ["AbCd1234"]


def test_ignores_duplicates_and_empty_bodies():
    body = "https://trello.com/c/AbCd1234 and again trello.com/c/AbCd1234"
    assert trello_sync.card_ids(body) == ["AbCd1234"]
    assert trello_sync.card_ids(None) == []


def test_skips_cleanly_without_secrets(monkeypatch, capsys):
    monkeypatch.delenv("TRELLO_KEY", raising=False)
    monkeypatch.delenv("TRELLO_TOKEN", raising=False)
    assert trello_sync.main() == 0
    assert "skipping" in capsys.readouterr().out
