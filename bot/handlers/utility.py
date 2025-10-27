"""Utility command handlers for the Telegram Group Management Bot.

This module implements generic helper commands such as a simple
calculator, time display, note taking, and user information lookup.
"""
from __future__ import annotations

import ast
import operator
from datetime import datetime
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    try:
        from telegram import Update  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping utility handlers")
        return

    # Allowed operators for safe evaluation
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def _eval_expr(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Operation not allowed")
            return allowed_operators[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Unary operation not allowed")
            return allowed_operators[type(node.op)](_eval_expr(node.operand))
        raise ValueError("Invalid expression")

    async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        parts = update.message.text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /calc <expression>")
            return
        expr = parts[1].replace(" ", "")
        try:
            node = ast.parse(expr, mode='eval').body
            result = _eval_expr(node)
            await update.message.reply_text(f"Result: {result}")
        except Exception:
            await update.message.reply_text("Invalid expression.")

    async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        await update.message.reply_text(f"Current time: {now}")

    async def note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        parts = update.message.text.split(None, 2)
        if len(parts) < 3:
            await update.message.reply_text("Usage: /note <title> <content>")
            return
        title = parts[1].strip().lower()
        content = parts[2].strip()
        notes = context.chat_data.setdefault("notes", {})
        user_notes = notes.setdefault(update.effective_user.id, {})
        user_notes[title] = content
        await update.message.reply_text(f"Note '{title}' saved.")

        
    async def getnote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        parts = update.message.text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /getnote <title>")
            return
        title = parts[1].strip().lower()
        notes = context.chat_data.get("notes", {})
        user_notes = notes.get(update.effective_user.id, {})
        if title in user_notes:
            await update.message.reply_text(user_notes[title])
        else:
            await update.message.reply_text("Note not found.")

    async def whois(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
        if not target:
            return
        text = (
            f"User: <b>{target.full_name}</b>\n"
            f"ID: <code>{target.id}</code>\n"
            f"Username: @{target.username}"
        )
        await update.message.reply_html(text)

    # Register handlers
    application.add_handler(CommandHandler("calc", calc))
    application.add_handler(CommandHandler(["time", "utc"], time_cmd))
    application.add_handler(CommandHandler("note", note))
    application.add_handler(CommandHandler("getnote", getnote))
    application.add_handler(CommandHandler("whois", whois))