"""Fun command handlers for the Telegram Group Management Bot.

This module implements playful commands such as dice rolls, coin flips,
compliments, jokes, quotes, roasts, and simple interactions like hug,
slap, kiss, and fight.  These commands are intended to add
entertainment value to group chats.
"""
from __future__ import annotations

import random
import json
from typing import Dict, Any, Optional, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


def _load_json_file(filename: str) -> List[str]:
    """Load a list of strings from a JSON file in the data package."""
    from importlib import resources
    try:
        with resources.open_text("bot.data", filename) as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed to load %s: %s", filename, exc)
        return []


COMPLIMENTS = _load_json_file("compliments.json")
JOKES = _load_json_file("jokes.json")
QUOTES = _load_json_file("quotes.json")
ROASTS = _load_json_file("roasts.json")


def register(application: Any, services: Dict[str, Any]) -> None:
    try:
        from telegram import Update, DiceEmoji  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping fun handlers")
        return

    async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Roll a dice using Telegram's built-in animation."""
        try:
            await context.bot.send_dice(update.effective_chat.id, emoji=DiceEmoji.DICE)
        except Exception as exc:
            logger.exception("Failed to send dice: %s", exc)
            await update.message.reply_text("Failed to roll a dice.")

    async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Flip a coin and return heads or tails."""
        result = random.choice(["Heads", "Tails"])
        await update.message.reply_text(f"Coin flip: {result}")

    async def _send_random(update: Update, items: List[str], label: str) -> None:
        if not items:
            await update.message.reply_text(f"No {label} available.")
            return
        await update.message.reply_text(random.choice(items))

    async def compliment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _send_random(update, COMPLIMENTS, "compliments")

    async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _send_random(update, JOKES, "jokes")

    async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _send_random(update, QUOTES, "quotes")

    async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _send_random(update, ROASTS, "roasts")

    def _name_of_target(update: Update) -> str:
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
        if target.username:
            return f"@{target.username}"
        return target.first_name

    async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        name = _name_of_target(update)
        await update.message.reply_text(f"{name}, you got a warm hug! 🤗")

    async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        name = _name_of_target(update)
        await update.message.reply_text(f"{name}, you've been slapped! 👋")

    async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        name = _name_of_target(update)
        await update.message.reply_text(f"{name}, here's a kiss! 😘")

    async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        name = _name_of_target(update)
        outcome = random.choice(["wins", "loses"])
        await update.message.reply_text(f"{name} {outcome} the fight! 🥊")

    # Register commands
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("coin", coin))
    application.add_handler(CommandHandler("compliment", compliment))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CommandHandler("quote", quote))
    application.add_handler(CommandHandler("roast", roast))
    application.add_handler(CommandHandler("hug", hug))
    application.add_handler(CommandHandler("slap", slap))
    application.add_handler(CommandHandler("kiss", kiss))
    application.add_handler(CommandHandler("fight", fight))