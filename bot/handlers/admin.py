"""Admin command handlers for the Telegram Group Management Bot.

This module implements commands for managing administrators within the
chat, such as promoting or demoting users.  Only existing admins can
run these commands.
"""
from __future__ import annotations

from typing import Dict, Any, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    """Register admin command handlers with the application."""
    try:
        from telegram import Update, ChatAdministratorRights  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping admin handlers")
        return

    async def _get_target_user(update: Update) -> Optional[int]:
        # Use the same helper logic as in moderation
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            return update.message.reply_to_message.from_user.id
        args = update.message.text.split()
        if len(args) > 1:
            candidate = args[1].lstrip("@")
            try:
                return int(candidate)
            except ValueError:
                return None
        return None

    async def _is_admin(update: Update, user_id: int) -> bool:
        chat = update.effective_chat
        if not chat:
            return False
        try:
            member = await chat.get_member(user_id)
            return member.status in ("administrator", "creator")
        except Exception:
            return False

    async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to promote (reply or mention).")
            return
        try:
            # Promote with default rights (change as needed)
            rights = ChatAdministratorRights(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_topics=True,
            )
            await context.bot.promote_chat_member(chat.id, target_id, rights)
            await update.message.reply_text("User has been promoted to admin.")
        except Exception as exc:
            logger.exception("Failed to promote user: %s", exc)
            await update.message.reply_text("Failed to promote user. Do I have sufficient rights?")

    async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        issuer_id = update.effective_user.id if update.effective_user else None
        if not issuer_id or not await _is_admin(update, issuer_id):
            await update.message.reply_text("You must be an admin to use this command.")
            return
        target_id = await _get_target_user(update)
        if not target_id:
            await update.message.reply_text("Please specify a user to demote (reply or mention).")
            return
        try:
            # Demote by setting all admin rights to False
            rights = ChatAdministratorRights(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_manage_topics=False,
            )
            await context.bot.promote_chat_member(chat.id, target_id, rights)
            await update.message.reply_text("User has been demoted.")
        except Exception as exc:
            logger.exception("Failed to demote user: %s", exc)
            await update.message.reply_text("Failed to demote user. Do I have sufficient rights?")

    # Register handlers
    application.add_handler(CommandHandler("promote", promote))
    application.add_handler(CommandHandler("demote", demote))