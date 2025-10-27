"""Utility subpackage for the Telegram Group Management Bot.

This package provides helper modules for logging, database connections,
and general convenience functions.  Modules are designed to defer heavy
imports until necessary so that importing the utils package does not
require optional dependencies such as SQLAlchemy.
"""