"""
Reward360 Transaction Intelligence Engine — Logger Setup

Configures Python's built-in logging module with two handlers:
  1. Console (INFO)  — shows progress during execution
  2. File (DEBUG)    — detailed log at logs/pipeline.log

The file log doubles as a prompt history: every LLM prompt and response
is logged at DEBUG level with timestamps, enabling post-run review.

Usage:
    from src.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Processing transaction: %s", raw_text)
"""

import logging
from src.config import LOGS_DIR, LOG_FILE


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.

    On first call, sets up the root 'reward360' logger with console and
    file handlers. Subsequent calls return child loggers under the same
    hierarchy so all modules share the same configuration.

    Args:
        name: Module name (typically __name__), used to identify log source.

    Returns:
        A configured logging.Logger instance.
    """
    # All project loggers live under the 'reward360' namespace
    logger = logging.getLogger(f"reward360.{name}")

    # Only configure handlers once (on the root reward360 logger)
    root_logger = logging.getLogger("reward360")
    if not root_logger.handlers:
        _setup_root_logger(root_logger)

    return logger


def _setup_root_logger(root_logger: logging.Logger) -> None:
    """
    Configure the root 'reward360' logger with console and file handlers.

    Called once on first get_logger() invocation. Subsequent calls are no-ops
    because we check for existing handlers.
    """
    root_logger.setLevel(logging.DEBUG)

    # Log format: [timestamp] [LEVEL] [module] message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Console handler (INFO level) ---
    # Shows progress updates without overwhelming detail
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # --- File handler (DEBUG level) ---
    # Captures everything including LLM prompts/responses for prompt history
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    root_logger.debug("Logger initialized. Log file: %s", LOG_FILE)
