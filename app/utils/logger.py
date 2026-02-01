"""
Logging Utilities for AI Research Crew Pro

Provides structured logging with configurable levels,
formatted output, and optional file logging.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config.settings import get_settings


class ColorFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",     # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        # Add color to level name
        record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    enable_color: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR). Defaults to settings.
        log_file: Optional path to log file for file logging.
        enable_color: Enable colored console output.
    """
    settings = get_settings()
    log_level = level or settings.log_level
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Format string
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    
    if enable_color and sys.stdout.isatty():
        console_handler.setFormatter(ColorFormatter(fmt, datefmt))
    else:
        console_handler.setFormatter(logging.Formatter(fmt, datefmt))
    
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(logging.Formatter(fmt, datefmt))
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name, typically __name__ from the calling module.
        
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)


class TaskLogger:
    """Context-aware logger for tracking task progress."""
    
    def __init__(self, task_name: str):
        self.logger = get_logger(f"task.{task_name}")
        self.task_name = task_name
        self.start_time = datetime.now()
    
    def start(self, message: str = "Starting task"):
        """Log task start."""
        self.start_time = datetime.now()
        self.logger.info(f"🚀 {message}")
    
    def progress(self, message: str, percentage: Optional[int] = None):
        """Log task progress."""
        if percentage is not None:
            self.logger.info(f"📊 [{percentage}%] {message}")
        else:
            self.logger.info(f"📊 {message}")
    
    def success(self, message: str = "Task completed"):
        """Log task success."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(f"✅ {message} (took {elapsed:.2f}s)")
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log task error."""
        if exception:
            self.logger.error(f"❌ {message}: {exception}", exc_info=True)
        else:
            self.logger.error(f"❌ {message}")
    
    def warning(self, message: str):
        """Log task warning."""
        self.logger.warning(f"⚠️ {message}")
