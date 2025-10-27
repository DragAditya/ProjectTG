"""Toggle command handlers for the Telegram Group Management Bot.

These commands enable or disable the bot's functionality in a chat or
modify its verbosity.  Only chat administrators can toggle these
settings.
"""
from __future__ import annotations

from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    try:
        from telegram import Update  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping toggle handlers")
        return

    async def _is_admin(update: Update) -> bool:
        chat = update.effective_chat
        user = update.effective_user
        if not chat or not user:
            return False
        try:
            member = await chat.get_member(user.id)
            return member.status in ("administrator", "creator")
        except Exception:
            return False

    async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await _is_admin(update):
            await update.message.reply_text("Only administrators can enable the bot.")
            return
        context.chat_data["enabled"] = True
        await update.message.reply_text("Bot is now enabled in this chat.")

    async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await _is_admin(update):
            await update.message.reply_text("Only administrators can disable the bot.")
            return
        context.chat_data["enabled"] = False
        await update.message.reply_text("Bot is now disabled in this chat.")

    async def silent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await _is_admin(update):
            await update.message.reply_text("Only administrators can toggle silent mode.")
            return
        current = context.chat_data.get("silent", False)
        context.chat_data["silent"] = not current
        state = "enabled" if context.chat_data["silent"] else "disabled"
        await update.message.reply_text(f"Silent mode is now {state}.")

    async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await _is_admin(update):
            await update.message.reply_text("Only administrators can toggle debug mode.")
            return
        current = context.chat_data.get("debug", False)
        context.chat_data["debug"] = not current
        state = "enabled" if context.chat_data["debug"] else "disabled"
        await update.message.reply_text(f"Debug mode is now {state}.")

    # Register commands (/on and /off are aliases)
    application.add_handler(CommandHandler(["enablebot", "on", "enable"], enable))
    application.add_handler(CommandHandler(["disablebot", "off", "disable"], disable))
    application.add_handler(CommandHandler("silent", silent))
    application.add_handler(CommandHandler("debug", debug))