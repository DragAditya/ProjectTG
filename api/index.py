"""
FastAPI entry point for Vercel and Render deployments.

This module exposes an ASGI application compatible with Vercel and
Render. It integrates the python‑telegram‑bot Application using
webhooks and configures a webhook URL dynamically based on the
deployment environment. The PTB application is initialised in the
lifespan context to ensure proper startup and shutdown behaviour.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application

from bot.config import BotConfig
from bot.main import register_handlers
from bot.services.gemini_api import GeminiService
from bot.services.weather_service import WeatherService
from bot.services.translation_service import TranslationService
from bot.services.dictionary_service import DictionaryService
from bot.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the FastAPI application.

    This context manager initialises the python‑telegram‑bot
    Application, configures external services, registers handlers,
    sets the webhook, and gracefully shuts down on exit.
    """
    # Load configuration from environment variables
    config = BotConfig.load()
    # Set up logging early to capture startup events
    logger = setup_logging(config.log_file)
    logger.info("Initialising PTB application for webhook deployment...")

    # Build PTB application without a built‑in updater (webhook mode)
    application = (
        Application.builder()
        .token(config.telegram_bot_token)
        .updater(None)
        .build()
    )

    # Store application in FastAPI state for access in route handlers
    app.state.application = application

    # Initialise external services and attach them to bot_data for handlers
    application.bot_data["gemini"] = GeminiService(config.gemini_api_key)
    application.bot_data["weather"] = WeatherService(config.weather_api_key)
    application.bot_data["translation"] = TranslationService(config.translation_api_key)
    application.bot_data["dictionary"] = DictionaryService(config.dictionary_api_key)

    # Register command and message handlers (implemented in bot.handlers)
    register_handlers(application)

    # Determine the base URL for webhook; priority: WEBHOOK_URL > VERCEL_URL > RENDER_EXTERNAL_URL
    base_url = os.getenv("WEBHOOK_URL") or os.getenv("VERCEL_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not base_url:
        logger.warning(
            "No base URL found for webhook. Set WEBHOOK_URL, VERCEL_URL, or RENDER_EXTERNAL_URL in your environment."
        )
    else:
        base_url = base_url.rstrip("/")
        webhook_url = f"{base_url}/api/webhook"
        try:
            await application.bot.setWebhook(webhook_url)
            logger.info("Webhook set to %s", webhook_url)
        except Exception as exc:
            logger.exception("Failed to set webhook: %s", exc)

    # Initialise the PTB application (starts internal resources)
    await application.initialize()
    await application.start()

    # Yield control back to FastAPI until shutdown
    try:
        yield
    finally:
        logger.info("Shutting down PTB application...")
        await application.stop()
        await application.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/api/webhook")
async def telegram_webhook(request: Request) -> Response:
    """Receive incoming Telegram updates via webhook and process them.

    Telegram will POST update payloads to this endpoint. The update
    is deserialised into a `telegram.Update` object and passed to
    `application.process_update`. The handler returns a simple JSON
    response acknowledging receipt.
    """
    application: Application = app.state.application  # type: ignore[assignment]
    try:
        update_data: Dict[str, Any] = await request.json()
    except Exception:
        # Invalid JSON should be ignored gracefully
        return Response(status_code=400, content="Invalid JSON")
    update: Update = Update.de_json(update_data, application.bot)
    await application.process_update(update)
    return Response(status_code=200, media_type="application/json", content="{}")


@app.get("/")
async def root() -> Dict[str, str]:
    """Health check endpoint.

    Returns a simple JSON object indicating that the service is
    running. Vercel automatically pings this route after deployment
    to determine if the function is alive.
    """
    return {"status": "ok"}