"""Moderation command handlers for the Telegram Group Management Bot.

This module implements commands for moderating the chat, such as banning,
kicking, muting users, and issuing warnings.  Most commands require
administrative privileges; the bot checks the invoking user's status
before performing potentially destructive actions.
"""
from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..utils.helpers import parse_duration, humanize_timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    """Register moderation command handlers with the application."""
    try:
        from telegram import Update, ChatPermissions  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping moderation handlers")
        return

    async def _get_target_user(update: Update) -> Optional[int]:
        """Extract the target user ID from a command.

        The target user can be specified by replying to a message or by passing
        a username or ID as the first argument.  Returns ``None`` if no
        target could be resolved.
        """
        # If the command is a reply, use the replied user
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            return update.message.reply_to_message.from_user.id
        # Otherwise, parse the first argument
        args = update.message.text.split()
        if len(args) > 1:
            candidate = args[1]
            # Remove '@' if present
            candidate = candidate.lstrip("@")
            try:
                # Try to convert to int (user ID)
                return int(candidate)
            except ValueError:
                # Try to get user by username from chat members
                # This requires Telegram API access; we skip username resolution here
                return None
        return None

    async def _is_admin(update: Update, user_id: int) -> bool:
        """Check whether a given user is an admin of the chat."""
        chat = update.effective_chat
        if not chat:
            return False
        try:
            member = await chat.get_member(user_id)
            return member.status in ("administrator", "creator")
        except Exception:
            return False

    async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Ban a user permanently from the chat."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to ban (reply or mention).")
            return
        try:
            await context.bot.ban_chat_member(chat.id, target_id)
            await update.message.reply_text("User has been banned.")
        except Exception as exc:
            logger.exception("Failed to ban user: %s", exc)
            await update.message.reply_text("Failed to ban user. Do I have sufficient rights?")

    async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Unban a previously banned user."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to unban (reply or mention).")
            return
        try:
            await context.bot.unban_chat_member(chat.id, target_id)
            await update.message.reply_text("User has been unbanned.")
        except Exception as exc:
            logger.exception("Failed to unban user: %s", exc)
            await update.message.reply_text("Failed to unban user. Do I have sufficient rights?")

    async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Kick a user from the chat (they can rejoin via invite link)."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to kick (reply or mention).")
            return
        try:
            # Kick by banning and immediately unbanning
            await context.bot.ban_chat_member(chat.id, target_id)
            await context.bot.unban_chat_member(chat.id, target_id)
            await update.message.reply_text("User has been kicked.")
        except Exception as exc:
            logger.exception("Failed to kick user: %s", exc)
            await update.message.reply_text("Failed to kick user. Do I have sufficient rights?")

    async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mute a user indefinitely or for a specified duration."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to mute (reply or mention).")
            return
        # Parse duration from second argument if provided
        args = update.message.text.split()
        duration = timedelta(weeks=1000)  # effectively forever
        if len(args) > 2:
            delta = parse_duration(args[2])
            if delta.total_seconds() > 0:
                duration = delta
        until_date = datetime.utcnow() + duration
        try:
            perms = ChatPermissions(can_send_messages=False)
            await context.bot.restrict_chat_member(chat.id, target_id, permissions=perms, until_date=until_date)
            text = "User has been muted."
            if duration.total_seconds() < 60 * 60 * 24 * 365:  # less than a year
                text += f" Mute duration: {humanize_timedelta(duration)}."
            await update.message.reply_text(text)
        except Exception as exc:
            logger.exception("Failed to mute user: %s", exc)
            await update.message.reply_text("Failed to mute user. Do I have sufficient rights?")

    async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Unmute a previously muted user."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to unmute (reply or mention).")
            return
        try:
            perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            await context.bot.restrict_chat_member(chat.id, target_id, permissions=perms)
            await update.message.reply_text("User has been unmuted.")
        except Exception as exc:
            logger.exception("Failed to unmute user: %s", exc)
            await update.message.reply_text("Failed to unmute user. Do I have sufficient rights?")

    async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Issue a warning to a user.  After 3 warnings, the user is kicked."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to warn (reply or mention).")
            return
        chat_data = context.chat_data.setdefault("warnings", {})
        count = chat_data.get(target_id, 0) + 1
        chat_data[target_id] = count
        await update.message.reply_text(f"User has been warned ({count}/3).")
        if count >= 3:
            try:
                await context.bot.ban_chat_member(chat.id, target_id)
                await context.bot.unban_chat_member(chat.id, target_id)
                chat_data[target_id] = 0  # reset warnings
                await update.message.reply_text("User has been kicked due to excessive warnings.")
            except Exception as exc:
                logger.exception("Failed to kick user after warnings: %s", exc)

    async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Remove a warning from a user."""
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to unwarn (reply or mention).")
            return
        chat_data = context.chat_data.setdefault("warnings", {})
        if chat_data.get(target_id, 0) > 0:
            chat_data[target_id] -= 1
            await update.message.reply_text(f"Removed a warning. Total warnings: {chat_data[target_id]}.")
        else:
            await update.message.reply_text("That user has no warnings.")

    async def warnlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List warnings for users in the chat."""
        chat_data = context.chat_data.get("warnings", {})
        if not chat_data:
            await update.message.reply_text("No warnings have been issued in this chat.")
            return
        lines = ["<b>Warnings:</b>"]
        for user_id, count in chat_data.items():
            lines.append(f"User {user_id}: {count} warning(s)")
        await update.message.reply_html("\n".join(lines))

    # Register handlers
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("kick", kick))
    application.add_handler(CommandHandler("mute", mute))
    application.add_handler(CommandHandler("unmute", unmute))
    application.add_handler(CommandHandler("warn", warn))
    application.add_handler(CommandHandler("unwarn", unwarn))
    application.add_handler(CommandHandler(["warns", "warnings"], warnlist))