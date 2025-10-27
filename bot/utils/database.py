"""Database utilities for the Telegram Group Management Bot.

This module provides an asynchronous SQLAlchemy engine and sessionmaker,
along with helper functions to initialize the database and obtain sessions.
Imports of ``sqlalchemy`` are deferred until necessary to avoid import
errors in environments where SQLAlchemy is not installed.  If the module
cannot be imported, a runtime error is raised when attempting to
initialize the database.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from .logger import get_logger

logger = get_logger(__name__)

# These variables will be set during database initialization
_async_session_maker: Optional[object] = None
Base: Optional[object] = None


async def init_db(database_url: str) -> None:
    """Initialize the asynchronous database engine and create tables.

    This function dynamically imports SQLAlchemy on first use.  It creates
    an asynchronous engine, constructs a sessionmaker, and creates any
    declarative tables defined under ``bot/utils/database`` or elsewhere in
    the project.  If SQLAlchemy is not installed, a RuntimeError is
    raised.

    Args:
        database_url: A SQLAlchemy database URL.  Defaults to a local
            SQLite database if not provided.

    Raises:
        RuntimeError: If SQLAlchemy cannot be imported or initialization
            fails.
    """
    global _async_session_maker, Base

    try:
        import importlib
        sqlalchemy_asyncio = importlib.import_module("sqlalchemy.ext.asyncio")
        sqlalchemy_orm = importlib.import_module("sqlalchemy.orm")
    except ImportError as exc:
        logger.error("SQLAlchemy must be installed to use the database: %s", exc)
        raise RuntimeError("SQLAlchemy is not installed.") from exc

    # Create the Base class for declarative models
    Base = sqlalchemy_orm.declarative_base()

    # Create async engine
    engine = sqlalchemy_asyncio.create_async_engine(
        database_url, echo=False, future=True
    )
    # Create async sessionmaker
    _async_session_maker = sqlalchemy_asyncio.async_sessionmaker(
        engine, expire_on_commit=False, class_=sqlalchemy_asyncio.AsyncSession
    )

    # Reflect models (import them here so they register with Base)
    # Placeholder: if you create models, import them here so Base.metadata knows
    # about them.  For example:
    # from .models import User
    # This file intentionally does not define models; see the handlers for
    # examples of simple in-memory storage instead.

    # Create tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created or verified successfully.")
    except Exception as exc:
        logger.exception("Error creating database tables: %s", exc)
        raise RuntimeError("Failed to initialize the database.") from exc


@asynccontextmanager
async def get_session() -> AsyncIterator[object]:
    """Asynchronously yield a database session.

    Example usage:

    ```python
    async with get_session() as session:
        # use session
        pass
    ```

    Yields:
        An AsyncSession instance for interacting with the database.

    Raises:
        RuntimeError: If the database has not been initialized.
    """
    if _async_session_maker is None:
        raise RuntimeError("Database has not been initialized. Call init_db() first.")
    session = _async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()