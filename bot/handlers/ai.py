"""AI and external information command handlers.

This module implements commands that leverage external services such as
Google's Gemini API, dictionary lookups, translation, and weather.
"""
from __future__ import annotations

from typing import Dict, Any, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    try:
        from telegram import Update  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping AI handlers")
        return

    gemini_service = services.get("gemini")
    weather_service = services.get("weather")
    translation_service = services.get("translation")
    dictionary_service = services.get("dictionary")

    async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Generate a response using the Gemini AI service."""
        if not gemini_service:
            await update.message.reply_text("AI service is not configured.")
            return
        prompt = update.message.text.split(None, 1)
        if len(prompt) < 2:
            await update.message.reply_text("Usage: /ai <your prompt>")
            return
        user_prompt = prompt[1]
        messages = [
            {"role": "user", "content": user_prompt},
        ]
        try:
            response_text = await gemini_service.chat(messages)
            await update.message.reply_text(response_text)
        except Exception as exc:
            logger.exception("AI command failed: %s", exc)
            await update.message.reply_text("Failed to generate a response.")

    async def define(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not dictionary_service:
            await update.message.reply_text("Dictionary service is not configured.")
            return
        parts = update.message.text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /define <word>")
            return
        word = parts[1].strip()
        data = await dictionary_service.define(word)
        if not data:
            await update.message.reply_text("No definition found.")
            return
        defs = data.get("definitions", [])
        if not defs:
            await update.message.reply_text("No definition found.")
            return
        lines = [f"<b>{word}</b> ({len(defs)} definitions):"]
        for item in defs[:3]:
            line = f"• <i>{item['part_of_speech']}</i>: {item['definition']}"
            if item.get("example"):
                line += f"\n  e.g., {item['example']}"
            lines.append(line)
        await update.message.reply_html("\n".join(lines))

    async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not translation_service:
            await update.message.reply_text("Translation service is not configured.")
            return
        parts = update.message.text.split(None, 2)
        if len(parts) < 3:
            await update.message.reply_text("Usage: /translate <lang> <text>")
            return
        target_lang = parts[1]
        text_to_translate = parts[2]
        data = await translation_service.translate(text_to_translate, target_lang)
        if not data:
            await update.message.reply_text("Translation failed.")
            return
        await update.message.reply_text(f"{data['translated']}")

    async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not weather_service:
            await update.message.reply_text("Weather service is not configured.")
            return
        parts = update.message.text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /weather <city>")
            return
        city = parts[1]
        data = await weather_service.get_weather(city)
        if not data:
            await update.message.reply_text("Couldn't retrieve weather data.")
            return
        text = (
            f"Weather in {data['city']}, {data['country']}:\n"
            f"{data['description'].capitalize()}\n"
            f"Temperature: {data['temperature']}°C\n"
            f"Humidity: {data['humidity']}%\n"
            f"Wind speed: {data['wind_speed']} m/s"
        )
        await update.message.reply_text(text)

    # Register commands
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("define", define))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("weather", weather))