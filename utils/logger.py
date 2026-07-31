"""Logging utilities for the Autonomous Job Agent."""
import logging
import sys
from pathlib import Path
from rich.logging import RichHandler


def setup_logger(name: str = "jobs_agent", level: str = "INFO") -> logging.Logger:
    """Configures structured console logging with Rich and log file handler.

    Args:
        name: Logger name identifier.
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    if not logger.handlers:
        # Rich console handler
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_path=False
        )
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(logs_dir / "agent.log", encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
