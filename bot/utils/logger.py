"""Logging utilities for the Telegram Group Management Bot.

This module configures a root logger that writes both to the console and
optionally to a file.  ANSI color codes are used for console output to
improve readability.  Log messages include timestamps, log levels,
module names, and the message body.
"""
import logging
import os
from logging import Logger

# ANSI escape codes for colored console output
ANSI_RESET = "\033[0m"
ANSI_COLORS = {
    logging.DEBUG: "\033[90m",    # Bright black
    logging.INFO: "\033[92m",     # Bright green
    logging.WARNING: "\033[93m",  # Bright yellow
    logging.ERROR: "\033[91m",    # Bright red
    logging.CRITICAL: "\033[95m", # Bright magenta
}


class ColorFormatter(logging.Formatter):
    """Custom formatter that applies ANSI colors to log levels."""

    def format(self, record: logging.LogRecord) -> str:
        color = ANSI_COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{ANSI_RESET}"


def setup_logging(log_file: str, level: int = logging.INFO) -> Logger:
    """Configure the root logger with console and file handlers.

    If the logger is already configured (e.g., by another call), this
    function returns the existing logger without reconfiguration.

    Args:
        log_file: Path to the log file.  If falsy, file logging is disabled.
        level: The logging level to use for the root logger.

    Returns:
        The configured root logger.
    """
    logger = logging.getLogger()
    if logger.handlers:
        # Already configured by a previous call
        return logger

    logger.setLevel(level)

    # Console handler with color formatting
    console_handler = logging.StreamHandler()
    console_formatter = ColorFormatter(
        fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (no color) if path provided
    if log_file:
        # Ensure directory exists
        directory = os.path.dirname(log_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> Logger:
    """Get a named logger configured with the root logger's handlers.

    Args:
        name: The logger name.

    Returns:
        A logger instance with the given name.
    """
    return logging.getLogger(name)