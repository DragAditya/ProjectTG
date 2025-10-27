"""Service to translate text using an external translation API.

This implementation uses the free MyMemory translation API as an
example.  It can be replaced with another provider by modifying the
``base_url`` and request parameters.  Network requests are executed
in a separate thread via ``asyncio.to_thread`` to keep the main loop
responsive.
"""
import asyncio
from typing import Optional, Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TranslationService:
    """Service wrapper for translating text between languages."""

    def __init__(self, api_key: Optional[str], base_url: str = "https://api.mymemory.translated.net/get"):
        self.api_key = api_key
        self.base_url = base_url

    async def translate(self, text: str, target_lang: str, *, source_lang: str = "auto") -> Dict[str, Any]:
        """Translate text from the source language to the target language.

        Args:
            text: The text to translate.
            target_lang: The target language code (e.g., "en", "es").
            source_lang: The source language code ("auto" by default).

        Returns:
            A dictionary containing the translated text and metadata.  Returns
            an empty dict on error.
        """
        params = {
            "q": text,
            "langpair": f"{source_lang}|{target_lang}",
        }
        # Some translation providers accept an API key parameter
        if self.api_key:
            params["key"] = self.api_key

        def fetch() -> Dict[str, Any]:
            try:
                import requests  # type: ignore[import]
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                translated = data.get("responseData", {}).get("translatedText", "")
                return {
                    "original": text,
                    "translated": translated,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }
            except Exception as exc:
                logger.exception("Translation API request failed: %s", exc)
                return {}

        return await asyncio.to_thread(fetch)