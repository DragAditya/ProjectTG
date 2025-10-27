"""
Entry point for the Telegram Group Management Bot.

This module defines the asynchronous coroutine ``run_bot`` which bootstraps the
application: it loads configuration, sets up logging, initializes the
database, instantiates service clients, registers command handlers, and
starts polling Telegram for updates.  All imports of heavy dependencies
(``python-telegram-bot``, ``google.genai``, etc.) occur within functions
to avoid import errors at module load time in environments where these
libraries are absent.  This design allows the module to be imported
without triggering import errors when running unit tests or other tooling.
"""
from __future__ import annotations

import asyncio
from typing import Dict, Any

from .config import BotConfig
from .utils.logger import setup_logging, get_logger
from .utils.database import init_db
from .services.gemini_api import GeminiService
from .services.weather_service import WeatherService
from .services.translation_service import TranslationService
from .services.dictionary_service import DictionaryService


async def _import_telegram_objects() -> Dict[str, Any]:
    """Dynamically import Telegram classes used by the bot.

    Returns a dictionary mapping names to imported classes.  If the
    ``python-telegram-bot`` library is not installed, this function raises
    ``ImportError``.

    Raises:
        ImportError: If ``python-telegram-bot`` cannot be imported.
    """
    try:
        from telegram.ext import Application, Defaults  # type: ignore[import]
        from telegram.constants import ParseMode  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "python-telegram-bot is required to run the bot. "
            "Please install it via 'pip install python-telegram-bot'."
        ) from exc
    return {
        "Application": Application,
        "Defaults": Defaults,
        "ParseMode": ParseMode,
    }


def _register_all_handlers(application: Any) -> None:
    """Import and register all handler modules.

    Each handler module defines a ``register`` function that accepts
    the application and the service registry.  If a module fails to import
    (for example, because optional dependencies are missing), a warning
    is logged but the bot continues to run with the remaining handlers.

    Args:
        application: The Telegram Application instance.
    """
    logger = get_logger(__name__)
    # Gather services from bot_data for convenience
    services = application.bot_data.get("services", {})

    handler_modules = [
        "basic",
        "moderation",
        "admin",
        "group",
        "info",
        "toggles",
        "security",
        "fun",
        "ai",
        "utility",
        "roleplay",
        "games",
    ]
    for mod_name in handler_modules:
        try:
            module = __import__(f"bot.handlers.{mod_name}", fromlist=["register"])
            if hasattr(module, "register"):
                module.register(application, services)
                logger.info("Registered handlers from bot.handlers.%s", mod_name)
        except Exception as exc:
            logger.warning(
                "Failed to register handlers from bot.handlers.%s: %s", mod_name, exc
            )


async def run_bot() -> None:
    """Asynchronously run the Telegram bot application.

    This function encapsulates the full lifecycle of the bot: loading
    configuration, initializing logging and the database, instantiating
    service clients, registering handlers, and running the polling loop.
    It gracefully handles shutdown and logs any exceptions.
    """
    # Load configuration
    config = BotConfig.load()

    # Set up logging
    logger = setup_logging(config.log_file)
    logger.info("Launching Telegram bot...")

    # Initialize the database
    try:
        await init_db(config.database_url)
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)
        return

    # Instantiate external services
    gemini_service = GeminiService(config.gemini_api_key)
    weather_service = WeatherService(config.weather_api_key)
    translation_service = TranslationService(config.translation_api_key)
    dictionary_service = DictionaryService(config.dictionary_api_key)

    # Dynamically import telegram classes
    try:
        tg_objs = await _import_telegram_objects()
    except ImportError as exc:
        logger.error("Cannot import python-telegram-bot: %s", exc)
        return

    Application = tg_objs["Application"]
    Defaults = tg_objs["Defaults"]
    ParseMode = tg_objs["ParseMode"]

    # Build the application
    application = (
        Application.builder()
        .token(config.telegram_bot_token)
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    # Store services in bot_data for access in handlers
    application.bot_data["services"] = {
        "gemini": gemini_service,
        "weather": weather_service,
        "translation": translation_service,
        "dictionary": dictionary_service,
    }

    # Register all handlers
    _register_all_handlers(application)

    # Global error handler
    async def error_handler(update, context):  # type: ignore[no-untyped-def]
        logger.exception(
            "Error while handling update (update=%s): %s", update, context.error
        )

    application.add_error_handler(error_handler)

    # Start the bot
    try:
        await application.initialize()
        await application.start()
        logger.info("Bot started. Listening for updates...")
        # PTB v20+ uses run_polling instead of start_polling.  We fall back
        # to updater.start_polling for backward compatibility.
        try:
            await application.bot.initialize()
        except Exception:
            # ignore
            pass
        # Start polling
        try:
            # python-telegram-bot v20+ provides run_polling method
            await application.run_polling()
        except AttributeError:
            # Fall back to updater.start_polling
            await application.updater.start_polling()
            # Keep running until externally stopped
            await application.updater.idle()
    finally:
        # Graceful shutdown
        try:
            await application.stop()
        finally:
            await application.shutdown()
            logger.info("Bot shut down.")


if __name__ == "__main__":
    asyncio.run(run_bot())