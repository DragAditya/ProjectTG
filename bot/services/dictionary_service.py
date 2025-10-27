"""Service to fetch dictionary definitions from an external API.

This implementation uses the free Dictionary API hosted at
``dictionaryapi.dev``.  The service supports asynchronous lookups and
returns structured definitions with parts of speech and examples.
"""
import asyncio
from typing import Optional, Dict, Any, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DictionaryService:
    """Service wrapper for looking up word definitions."""

    def __init__(self, api_key: Optional[str], base_url: str = "https://api.dictionaryapi.dev/api/v2/entries"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def define(self, word: str, *, language: str = "en") -> Dict[str, Any]:
        """Look up definitions for a word in the specified language.

        Args:
            word: The word to define.
            language: The language code (default "en").

        Returns:
            A dict containing the word, language, and a list of definitions.
            Returns an empty dict on error.
        """
        url = f"{self.base_url}/{language}/{word}"

        def fetch() -> Dict[str, Any]:
            try:
                import requests  # type: ignore[import]
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data: List[Dict[str, Any]] = response.json()
                definitions: List[Dict[str, Any]] = []
                for meaning in data[0].get("meanings", []):
                    part_of_speech = meaning.get("partOfSpeech")
                    for definition in meaning.get("definitions", []):
                        definitions.append(
                            {
                                "part_of_speech": part_of_speech,
                                "definition": definition.get("definition"),
                                "example": definition.get("example"),
                            }
                        )
                return {
                    "word": word,
                    "language": language,
                    "definitions": definitions,
                }
            except Exception as exc:
                logger.exception("Dictionary API request failed: %s", exc)
                return {}

        return await asyncio.to_thread(fetch)