"""Roleplay command handlers for the Telegram Group Management Bot.

This module implements simple gamification commands to display a user's
experience points and generate a leaderboard.  XP accumulation is not
implemented and defaults to zero for all users.
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
        logger.warning("python-telegram-bot is not available; skipping roleplay handlers")
        return

    async def xp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        xp_data = context.chat_data.setdefault("xp", {})
        user_xp = xp_data.get(user_id, 0)
        await update.message.reply_text(f"Your XP: {user_xp}")

    async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        xp_data = context.chat_data.get("xp", {})
        user_xp = xp_data.get(user_id, 0)
        # Compute rank by sorted XP
        sorted_users = sorted(xp_data.items(), key=lambda kv: kv[1], reverse=True)
        rank_pos = next((i for i, (uid, _) in enumerate(sorted_users, start=1) if uid == user_id), None)
        if rank_pos is None:
            rank_pos = len(sorted_users) + 1
        await update.message.reply_text(f"Your rank: {rank_pos}\nYour XP: {user_xp}")

    async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        xp_data = context.chat_data.get("xp", {})
        if not xp_data:
            await update.message.reply_text("No XP data yet.")
            return
        sorted_users = sorted(xp_data.items(), key=lambda kv: kv[1], reverse=True)[:10]
        lines = ["<b>Leaderboard</b>"]
        for i, (uid, xp_value) in enumerate(sorted_users, start=1):
            lines.append(f"{i}. User {uid}: {xp_value} XP")
        await update.message.reply_html("\n".join(lines))

    # Register commands
    application.add_handler(CommandHandler("xp", xp))
    application.add_handler(CommandHandler("rank", rank))
    application.add_handler(CommandHandler("leaderboard", leaderboard))