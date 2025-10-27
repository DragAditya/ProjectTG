"""Top-level package for the Telegram Group Management Bot.

Importing this package exposes the ``run_bot`` coroutine from ``bot.main``.

Example:
    from bot import run_bot
    import asyncio

    asyncio.run(run_bot())
"""

from .main import run_bot  # noqa: F401