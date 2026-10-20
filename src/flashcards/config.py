"""Loads settings from environment variables and the local .env file.

The API key is never written in the code. It lives in .env, which is listed
in .gitignore, so it stays on this computer and never reaches GitHub.
"""

import os
from dataclasses import dataclass

from dotenv import dotenv_values

DEFAULT_MODEL = "gpt-4o-mini"
PLACEHOLDER_KEY = "sk-your-key-here"


class MissingApiKeyError(RuntimeError):
    pass


@dataclass
class Settings:
    api_key: str
    model: str


def load_settings(dotenv_path=".env"):
    """Read OPENAI_API_KEY and OPENAI_MODEL.

    A real environment variable wins; otherwise the value comes from .env.
    """
    file_values = dotenv_values(dotenv_path)

    def get(name):
        return (os.getenv(name) or file_values.get(name) or "").strip()

    api_key = get("OPENAI_API_KEY")
    if not api_key or api_key == PLACEHOLDER_KEY:
        raise MissingApiKeyError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and paste your key into it."
        )
    return Settings(api_key=api_key, model=get("OPENAI_MODEL") or DEFAULT_MODEL)
