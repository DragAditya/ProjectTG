"""Game command handlers for the Telegram Group Management Bot.

This module implements simple interactive games and virtual currency
commands.  Commands include a trivia quiz and a coin balance system.
"""
from __future__ import annotations

import random
from typing import Dict, Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


def register(application: Any, services: Dict[str, Any]) -> None:
    try:
        from telegram import Update  # type: ignore[import]
        from telegram.ext import CommandHandler, ContextTypes  # type: ignore[import]
    except ImportError:
        logger.warning("python-telegram-bot is not available; skipping game handlers")
        return

    async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start a simple trivia quiz."""
        questions = [
            ("What is the capital of France?", "paris"),
            ("Who wrote '1984'?", "george orwell"),
            ("What is 5 + 7?", "12"),
        ]
        q, a = random.choice(questions)
        context.chat_data["quiz_answer"] = a
        await update.message.reply_text(f"Quiz: {q}\nReply with /answer <your answer>")

    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        parts = update.message.text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Usage: /answer <your answer>")
            return
        expected = context.chat_data.pop("quiz_answer", None)
        if expected is None:
            await update.message.reply_text("No quiz in progress. Use /quiz to start one.")
            return
        if parts[1].strip().lower() == expected:
            await update.message.reply_text("Correct!")
        else:
            await update.message.reply_text(f"Wrong. The correct answer was: {expected}")

    async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        bank = context.chat_data.setdefault("bank", {})
        bal = bank.get(user_id, 0)
        await update.message.reply_text(f"Your balance: {bal} coins")

    async def give(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        parts = update.message.text.split()
        if len(parts) < 3:
            await update.message.reply_text("Usage: /give <user_id> <amount>")
            return
        try:
            target_id = int(parts[1])
            amount = int(parts[2])
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("Invalid usage. Amount must be a positive integer.")
            return
        bank = context.chat_data.setdefault("bank", {})
        sender_id = update.effective_user.id
        sender_bal = bank.get(sender_id, 0)
        if sender_bal < amount:
            await update.message.reply_text("Insufficient funds.")
            return
        bank[sender_id] = sender_bal - amount
        bank[target_id] = bank.get(target_id, 0) + amount
        await update.message.reply_text(f"Transferred {amount} coins to {target_id}.")

    async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show available items in the shop."""
        items = {
            "coffee": 10,
            "cookie": 5,
            "cake": 20,
        }
        lines = ["<b>Shop Items</b>"]
        for item, price in items.items():
            lines.append(f"{item.capitalize()}: {price} coins")
        await update.message.reply_html("\n".join(lines))

    # Register handlers
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("answer", answer))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("give", give))
    application.add_handler(CommandHandler("shop", shop))