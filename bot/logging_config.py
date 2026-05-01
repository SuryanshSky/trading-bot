"""
Logging configuration for the trading bot.

Sets up:
- A rotating file handler → logs/trading_bot.log
- A coloured console handler for INFO+ messages
"""

import logging
import logging.handlers
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"

# Colour codes for the console handler
_COLOURS = {
    logging.DEBUG:    "\033[36m",   # cyan
    logging.INFO:     "\033[32m",   # green
    logging.WARNING:  "\033[33m",   # yellow
    logging.ERROR:    "\033[31m",   # red
    logging.CRITICAL: "\033[35m",   # magenta
}
_RESET = "\033[0m"


class _ColouredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        colour = _COLOURS.get(record.levelno, "")
        message = super().format(record)
        return f"{colour}{message}{_RESET}"


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Call once at application startup.

    - DEBUG and above go to the log file (persistent, rotated at 5 MB).
    - INFO and above are printed to the console with colour.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid adding duplicate handlers if called more than once
    if root.handlers:
        return

    # --- File handler (DEBUG+) -------------------------------------------
    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)

    # --- Console handler (INFO+) -----------------------------------------
    console_fmt = _ColouredFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_fmt)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
