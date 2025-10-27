"""Integration with Google's Gemini API via the ``google-genai`` SDK.

This service provides asynchronous methods to generate AI responses
using the Gemini models.  It defers importing the ``google-genai``
package until runtime and gracefully handles missing dependencies or
request failures.
"""
from __future__ import annotations

from typing import List, Dict, Optional, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Service wrapper for Google's Gemini API.

    Args:
        api_key: API key for Gemini.  Required.
        model_name: Name of the model.  Defaults to ``"models/gemini-pro"``.
    """

    def __init__(self, api_key: str, model_name: str = "models/gemini-pro") -> None:
        if not api_key:
            raise ValueError("Gemini API key must be provided.")
        self.api_key = api_key
        self.model_name = model_name
        self.model: Optional[Any] = None
        # Attempt to configure the client.  The import may fail if the
        # google-genai package is not installed.  In that case, the
        # ``chat`` method will return a fallback message.
        try:
            import google.genai as genai  # type: ignore[import]
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as exc:
            logger.warning(
                "Unable to initialize google-genai; Gemini features will be disabled: %s", exc
            )
            self.model = None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        safety_settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a response from the Gemini model based on a chat history.

        The chat history is a list of dictionaries with keys ``"role"``
        (either ``"user"`` or ``"assistant"``) and ``"content"``.  This
        signature mirrors the OpenAI chat completion API for convenience.

        If the underlying model is unavailable (because the
        ``google-genai`` package is missing or failed to initialize), a
        generic fallback message is returned instead of raising an
        exception.

        Args:
            messages: List of message dicts containing the conversation history.
            max_tokens: Maximum number of tokens in the reply.
            temperature: Sampling temperature (0.0–1.0).
            top_p: Nucleus sampling parameter.
            safety_settings: Optional safety settings dict for the API.

        Returns:
            The generated response text, or a fallback message on error.
        """
        # If the model failed to initialize, return a default message
        if self.model is None:
            return "I'm sorry, the AI service is not available right now."

        # Build generation configuration
        generation_config: Dict[str, Any] = {
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_tokens,
        }
        if safety_settings:
            generation_config["safety_settings"] = safety_settings

        try:
            # google-genai uses ``generate_content_async`` to perform async calls
            response = await self.model.generate_content_async(
                messages=messages,
                generation_config=generation_config,
            )
            # Extract the first candidate
            candidates = getattr(response, "candidates", None)
            if candidates:
                content = candidates[0].content
                if isinstance(content, str):
                    return content.strip()
            logger.warning("Gemini API returned no usable candidates.")
            return "I'm sorry, I couldn't generate a response."
        except Exception as exc:
            logger.exception("Gemini API error: %s", exc)
            return "I'm sorry, something went wrong with the AI service."