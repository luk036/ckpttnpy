"""
Logging configuration for ckpttnpy.

This module provides centralized logging setup with structured logging levels
and formatters suitable for both development and production use.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Configure logging for the application.

    Args:
        log_level: Minimum logging level (default: INFO)
        log_file: Optional file path for log output
        format_string: Custom format string (default: structured format)

    Returns:
        Configured root logger instance

    Example:
        >>> setup_logging(logging.DEBUG)
        >>> logger = logging.getLogger(__name__)
        >>> logger.debug("Debug message")
    """
    if format_string is None:
        format_string = "[%(asctime)s] %(levelname)s:%(name)s:%(funcName)s:%(message)s"

    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    for handler in handlers:
        root_logger.addHandler(handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name, typically __name__ of the module

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Partitioning started")
    """
    return logging.getLogger(name)
