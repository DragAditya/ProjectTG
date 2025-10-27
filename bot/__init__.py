"""Top-level package for the Telegram Group Management Bot.

Importing this package exposes the ``run_bot`` coroutine from ``bot.main``.

Example:
    from bot import run_bot
    import asyncio

    asyncio.run(run_bot())
"""

# Alias run_bot to the synchronous main() for backward compatibility.
from .main import main as run_bot  # noqa: F401 
