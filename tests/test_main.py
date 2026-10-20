from main import main, parse_args


def test_default_options():
    args = parse_args(["notes.txt"])
    assert args.document == "notes.txt"
    assert args.max_cards == 10
    assert args.out is None


def test_missing_api_key_exits_with_an_error(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)  # no .env file here
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    notes = tmp_path / "notes.txt"
    notes.write_text("Some notes.", encoding="utf-8")
    assert main([str(notes)]) == 1
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().err
