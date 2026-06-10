"""Tests for the logging_config module."""

import logging
import os
import tempfile

import pytest

from ckpttnpy.logging_config import get_logger, setup_logging


class TestSetupLogging:
    """Tests for the setup_logging() function."""

    def test_setup_logging_defaults(self) -> None:
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self) -> None:
        logger = setup_logging(log_level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_setup_logging_removes_existing_handlers(self) -> None:
        logger1 = setup_logging(logging.WARNING)
        handler_count_before = len(logger1.handlers)
        logger2 = setup_logging(logging.INFO)
        handler_count_after = len(logger2.handlers)
        assert handler_count_after <= handler_count_before + 1

    def test_setup_logging_custom_format(self) -> None:
        custom_fmt = "%(name)s - %(levelname)s - %(message)s"
        logger = setup_logging(
            log_level=logging.ERROR, format_string=custom_fmt
        )
        assert isinstance(logger, logging.Logger)

    def test_setup_logging_with_file(self) -> None:
        log_path = tempfile.mktemp(suffix=".log")
        try:
            logger = setup_logging(
                log_level=logging.DEBUG, log_file=log_path
            )
            test_msg = "test_file_logging_message_12345"
            logger.info(test_msg)
            for h in logger.handlers:
                h.flush()
                h.close()
            logging.getLogger().handlers.clear()
            with open(log_path) as f:
                content = f.read()
            assert test_msg in content
        finally:
            if os.path.exists(log_path):
                os.remove(log_path)

    def test_setup_logging_without_file(self) -> None:
        logger = setup_logging(logging.INFO)
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 0


class TestGetLogger:
    """Tests for the get_logger() function."""

    def test_get_logger_returns_logger(self) -> None:
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_propagates(self) -> None:
        logger = get_logger("test_module")
        assert logger.propagate


class TestIntegration:
    """Integration tests combining setup_logging and get_logger."""

    def test_logger_uses_configured_level(self) -> None:
        _ = setup_logging(log_level=logging.WARNING)
        logger = get_logger("integration_test")
        root = logging.getLogger()
        assert root.level == logging.WARNING
        assert logger.isEnabledFor(logging.WARNING)
        assert not logger.isEnabledFor(logging.DEBUG)


if __name__ == "__main__":
    pytest.main([__file__])
