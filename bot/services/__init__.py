"""Service subpackage for the Telegram Group Management Bot.

This package contains wrappers around external APIs used by the bot.
Each service module is responsible for handling network requests,
authentication, and error handling for a specific API.  Services are
instantiated in ``bot.main`` and stored in ``application.bot_data`` for
use by command handlers.
"""