"""
Logging configuration for the application.
"""

import logging
import logging.handlers
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_DIR

# Create logger
logger = logging.getLogger("business_monitor")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler
log_file = LOG_DIR / "app.log"
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=10*1024*1024, backupCount=5
)
file_handler.setLevel(getattr(logging, LOG_LEVEL))
file_handler.setFormatter(detailed_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))
console_handler.setFormatter(detailed_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"business_monitor.{name}")
