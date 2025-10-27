"""Group management command handlers for the Telegram Group Management Bot.

This module implements commands that manage the chat state and content,
including pinning/unpinning messages, purging multiple messages, setting
welcome messages and rules, and tagging all members.
"""
from __future__ import annotations

from typing import Dict, Any, Optional

from ..utils.logger import get_logger
from ..utils.helpers import escape_html

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    try:
        from telegram import Update  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping group handlers")
        return

    async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        issuer = update.effective_user
        if not issuer or not (await chat.get_member(issuer.id)).status in ("administrator", "creator"):
            await update.message.reply_text("You must be an admin to pin messages.")
            return
        if not update.message.reply_to_message:
            await update.message.reply_text("Reply to a message you want to pin.")
            return
        try:
            await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id, disable_notification=True)
            await update.message.reply_text("Message pinned.")
        except Exception as exc:
            logger.exception("Failed to pin message: %s", exc)
            await update.message.reply_text("Failed to pin message. Do I have sufficient rights?")

    async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        issuer = update.effective_user
        if not issuer or not (await chat.get_member(issuer.id)).status in ("administrator", "creator"):
            await update.message.reply_text("You must be an admin to unpin messages.")
            return
        # If reply, unpin that message; else unpin last pinned
        msg_id = update.message.reply_to_message.message_id if update.message.reply_to_message else None
        try:
            if msg_id:
                await context.bot.unpin_chat_message(chat.id, message_id=msg_id)
            else:
                await context.bot.unpin_all_chat_messages(chat.id)
            await update.message.reply_text("Message(s) unpinned.")
        except Exception as exc:
            logger.exception("Failed to unpin message: %s", exc)
            await update.message.reply_text("Failed to unpin message.")

    async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Delete a range of messages. Use by replying to a message and invoking /purge."""
        chat = update.effective_chat
        if not chat:
            return
        issuer = update.effective_user
        if not issuer or not (await chat.get_member(issuer.id)).status in ("administrator", "creator"):
            await update.message.reply_text("You must be an admin to purge messages.")
            return
        if not update.message.reply_to_message:
            await update.message.reply_text("Reply to a message to purge from that message up to the current one.")
            return
        from_id = update.message.reply_to_message.message_id
        to_id = update.message.message_id
        try:
            for msg_id in range(from_id, to_id + 1):
                try:
                    await context.bot.delete_message(chat.id, msg_id)
                except Exception:
                    # Ignore individual delete failures
                    continue
            await context.bot.send_message(chat.id, "Messages purged.")
        except Exception as exc:
            logger.exception("Failed to purge messages: %s", exc)
            await update.message.reply_text("Failed to purge messages.")

    async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set the welcome message for the group."""
        chat_data = context.chat_data
        text = update.message.text
        parts = text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /setwelcome Your welcome message here.")
            return
        welcome_msg = parts[1]
        chat_data["welcome_message"] = welcome_msg
        await update.message.reply_text("Welcome message set.")

    async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show the current welcome message."""
        chat_data = context.chat_data
        welcome_msg = chat_data.get("welcome_message")
        if welcome_msg:
            await update.message.reply_html(escape_html(welcome_msg))
        else:
            await update.message.reply_text("No welcome message has been set.")

    async def setrules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set the rules for the group."""
        chat_data = context.chat_data
        parts = update.message.text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /setrules The rules of this group.")
            return
        rules = parts[1]
        chat_data["rules"] = escape_html(rules)
        await update.message.reply_text("Rules have been updated.")

    async def tagall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Tag all members in the chat.  Disabled by default to avoid spam."""
        await update.message.reply_text("Tagging all members is disabled to prevent spam.")

    # Register handlers
    application.add_handler(CommandHandler("pin", pin))
    application.add_handler(CommandHandler("unpin", unpin))
    application.add_handler(CommandHandler("purge", purge))
    application.add_handler(CommandHandler("setwelcome", setwelcome))
    application.add_handler(CommandHandler("welcome", welcome))
    application.add_handler(CommandHandler("setrules", setrules))
    application.add_handler(CommandHandler("tagall", tagall))