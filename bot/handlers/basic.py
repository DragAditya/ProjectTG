"""Basic command handlers for the Telegram Group Management Bot.

This module implements simple, universal commands such as ``/start``,
``/help``, ``/ping``, and ``/rules``.  Handlers defined here are
available in all chats and do not require administrative privileges.
"""
from __future__ import annotations

from typing import Dict, Any, List

from ..utils.helpers import escape_html
from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    """Register basic command handlers with the application.

    Args:
        application: The Telegram Application to register handlers on.
        services: A dict of service instances (unused here but kept for
            signature consistency).
    """
    try:
        from telegram import Update  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping basic handlers")
        return

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command.
        Sends a greeting and informs the user about /help."""
        user = update.effective_user
        name = escape_html(user.first_name or user.username or "there") if user else "there"
        await update.message.reply_html(
            f"Hello, <b>{name}</b>! I'm here to help manage this group. "
            "Use /help to see what I can do."
        )

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command.
        Provides a brief overview of available commands."""
        # Build a help message dynamically based on registered commands
        commands: List[str] = []
        for handler in application.handlers.get(0, []):
            # Only include CommandHandlers
            if hasattr(handler, "commands"):
                commands.extend(handler.commands)
        commands = sorted(set(commands))
        text = "<b>Available commands:</b>\n" + ", ".join(f"/{cmd}" for cmd in commands)
        await update.message.reply_html(text)

    async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /ping command.
        Replies with 'Pong!'."""
        await update.message.reply_text("Pong!")

    async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /rules command.
        Displays the group's rules if set by /setrules."""
        chat_data = context.chat_data
        group_rules: str = chat_data.get("rules", "No rules have been set for this group.")
        await update.message.reply_html(group_rules)

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("rules", rules))