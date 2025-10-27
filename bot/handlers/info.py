"""Information command handlers for the Telegram Group Management Bot.

This module implements commands that retrieve information about users
and chats, such as IDs, warning counts, and reporting messages.
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
        logger.warning("python-telegram-bot is not available; skipping info handlers")
        return

    async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show chat and user IDs."""
        chat_id = update.effective_chat.id if update.effective_chat else None
        user_id = update.effective_user.id if update.effective_user else None
        text = f"Chat ID: <code>{chat_id}</code>\nUser ID: <code>{user_id}</code>"
        await update.message.reply_html(text)

    async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Display basic info about a user and their warning count."""
        if not update.effective_chat:
            return
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
        if not target:
            return
        warnings = context.chat_data.get("warnings", {}).get(target.id, 0)
        text = (
            f"User: <b>{target.full_name}</b>\n"
            f"ID: <code>{target.id}</code>\n"
            f"Username: @{target.username}\n"
            f"Warnings: {warnings}"
        )
        await update.message.reply_html(text)

    async def lastactive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show when the user was last active.  Placeholder implementation."""
        await update.message.reply_text("I do not track activity yet.")

    async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Report a message to chat admins by tagging them.  Placeholder implementation."""
        chat = update.effective_chat
        if not chat:
            return
        # Fetch administrators and mention them
        try:
            admins = await chat.get_administrators()
            mentions = []
            for admin in admins:
                user = admin.user
                if user.is_bot:
                    continue
                if user.username:
                    mentions.append(f"@{user.username}")
                else:
                    mentions.append(f"<a href=\"tg://user?id={user.id}\">{user.first_name}</a>")
            mention_text = " ".join(mentions) if mentions else "(no admins)"
            await update.message.reply_html(f"Reported to admins: {mention_text}")
        except Exception as exc:
            logger.exception("Failed to report message: %s", exc)
            await update.message.reply_text("Failed to report message.")

    # Register handlers
    application.add_handler(CommandHandler("id", id_cmd))
    application.add_handler(CommandHandler("user", user_info))
    application.add_handler(CommandHandler("lastactive", lastactive))
    application.add_handler(CommandHandler("report", report))