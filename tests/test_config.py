import pytest

from flashcards.config import DEFAULT_MODEL, MissingApiKeyError, load_settings


@pytest.fixture
def no_dotenv(tmp_path):
    """Point at a .env file that doesn't exist, so tests only see what they set."""
    return tmp_path / "missing.env"


def test_reads_key_and_model_from_environment(monkeypatch, no_dotenv):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    settings = load_settings(no_dotenv)
    assert settings.api_key == "sk-test-123"
    assert settings.model == "gpt-test"


def test_model_defaults_to_gpt_4o_mini(monkeypatch, no_dotenv):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert load_settings(no_dotenv).model == DEFAULT_MODEL


def test_missing_key_gives_a_clear_error(monkeypatch, no_dotenv):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(MissingApiKeyError, match="Copy .env.example"):
        load_settings(no_dotenv)


def test_placeholder_key_is_rejected(monkeypatch, no_dotenv):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-your-key-here")
    with pytest.raises(MissingApiKeyError):
        load_settings(no_dotenv)


def test_key_can_come_from_a_dotenv_file(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-from-file\n")
    assert load_settings(env_file).api_key == "sk-from-file"
