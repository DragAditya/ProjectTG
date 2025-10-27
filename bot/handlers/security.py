"""Security command handlers for the Telegram Group Management Bot.

This module implements commands for locking or unlocking certain types of
content (e.g., media, stickers) in the chat.  The bot stores the
locked types in the chat's ``chat_data``; enforcement is not
implemented in this version but can be added by filtering messages in
message handlers.
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
        logger.warning("python-telegram-bot is not available; skipping security handlers")
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

    async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await _is_admin(update):
            await update.message.reply_text("Only administrators can lock content types.")
            return
        parts = update.message.text.split()
        if len(parts) < 2:
            await update.message.reply_text("Usage: /lock <type> [type...] (e.g., media links gifs)")
            return
        types = [t.lower() for t in parts[1:]]
        locks = context.chat_data.setdefault("locks", set())
        locks.update(types)
        await update.message.reply_text(f"Locked types: {', '.join(sorted(locks))}")

    async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await _is_admin(update):
            await update.message.reply_text("Only administrators can unlock content types.")
            return
        parts = update.message.text.split()
        if len(parts) < 2:
            await update.message.reply_text("Usage: /unlock <type> [type...] (e.g., media links gifs)")
            return
        types = [t.lower() for t in parts[1:]]
        locks = context.chat_data.setdefault("locks", set())
        for t in types:
            locks.discard(t)
        await update.message.reply_text(f"Locked types: {', '.join(sorted(locks)) if locks else 'none'}")

    async def locks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        locks = context.chat_data.get("locks", set())
        if locks:
            await update.message.reply_text(f"Locked types: {', '.join(sorted(locks))}")
        else:
            await update.message.reply_text("No content types are locked.")

    # Register commands
    application.add_handler(CommandHandler("lock", lock))
    application.add_handler(CommandHandler("unlock", unlock))
    application.add_handler(CommandHandler(["locks", "showlocks"], locks))