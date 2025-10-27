"""Configuration loader for the Telegram Group Management Bot.

This module defines a dataclass ``BotConfig`` that encapsulates all configuration
values required by the bot. It loads values from environment variables and
optionally uses ``python-dotenv`` to read from a ``.env`` file when present.

If required variables are missing, a ``RuntimeError`` is raised.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _load_dotenv_if_available() -> None:
    """Attempt to load environment variables from a .env file.

    This function tries to import ``dotenv.load_dotenv`` from ``python-dotenv``.  If
    the module is not installed, it silently does nothing.
    """
    try:
        from dotenv import load_dotenv  # type: ignore[import]
    except Exception:
        # Missing python-dotenv is not fatal; environment variables must be provided
        return
    load_dotenv()


@dataclass(frozen=True)
class BotConfig:
    """Dataclass holding configuration values for the bot.

    Attributes:
        telegram_bot_token: Telegram API token for the bot.
        gemini_api_key: API key for Google Gemini.
        weather_api_key: Optional API key for the weather service.
        translation_api_key: Optional API key for translation.
        dictionary_api_key: Optional API key for dictionary lookups.
        database_url: SQLAlchemy database URL (default uses SQLite).
        log_file: Path to the log file for persistent logging.
    """

    telegram_bot_token: str
    gemini_api_key: str
    weather_api_key: Optional[str] = None
    translation_api_key: Optional[str] = None
    dictionary_api_key: Optional[str] = None
    database_url: str = "sqlite+aiosqlite:///./bot.db"
    log_file: str = "bot.log"

    @classmethod
    def load(cls) -> "BotConfig":
        """Load configuration from the current environment.

        This method reads environment variables, optionally loading them from a
        `.env` file.  Required variables must be present or a RuntimeError
        will be thrown.

        Returns:
            BotConfig: A populated configuration dataclass.

        Raises:
            RuntimeError: If required configuration values are missing.
        """
        # Load from .env if possible
        _load_dotenv_if_available()

        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            raise RuntimeError("Missing required environment variable: TELEGRAM_BOT_TOKEN")

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise RuntimeError("Missing required environment variable: GEMINI_API_KEY")

        weather_api_key = os.getenv("WEATHER_API_KEY")
        translation_api_key = os.getenv("TRANSLATION_API_KEY")
        dictionary_api_key = os.getenv("DICTIONARY_API_KEY")
        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")
        log_file = os.getenv("LOG_FILE", "bot.log")

        return cls(
            telegram_bot_token=telegram_bot_token,
            gemini_api_key=gemini_api_key,
            weather_api_key=weather_api_key,
            translation_api_key=translation_api_key,
            dictionary_api_key=dictionary_api_key,
            database_url=database_url,
            log_file=log_file,
        )