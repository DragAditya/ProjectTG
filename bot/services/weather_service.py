"""Service to fetch weather information from an external API.

This implementation uses OpenWeatherMap as a reference but can be
adapted to any provider.  Network requests are executed in a separate
thread via ``asyncio.to_thread`` to avoid blocking the event loop.
If the API key is not provided, calls to ``get_weather`` will return
an empty dictionary and log a warning.
"""
import asyncio
from typing import Optional, Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class WeatherService:
    """Service wrapper for fetching weather data from an external API."""

    def __init__(self, api_key: Optional[str], base_url: str = "https://api.openweathermap.org/data/2.5/weather"):
        self.api_key = api_key
        self.base_url = base_url

    async def get_weather(self, city: str, *, units: str = "metric", lang: str = "en") -> Dict[str, Any]:
        """Fetch current weather data for a given city.

        Args:
            city: The name of the city.
            units: Measurement units ("metric" or "imperial").
            lang: Language for the weather description.

        Returns:
            A dictionary containing weather information.  Returns an empty
            dictionary if the API key is missing or if an error occurs.
        """
        if not self.api_key:
            logger.warning("Weather API key is not configured. Skipping weather request.")
            return {}

        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
            "lang": lang,
        }

        def fetch() -> Dict[str, Any]:
            try:
                # Import requests lazily to avoid a hard dependency at module import time
                import requests  # type: ignore[import]
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "city": data.get("name"),
                    "country": data.get("sys", {}).get("country"),
                }
            except Exception as exc:
                logger.exception("Weather API request failed: %s", exc)
                return {}

        return await asyncio.to_thread(fetch)