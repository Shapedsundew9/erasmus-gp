"""Tests for the egp_log module."""

import unittest
from logging import Logger, NullHandler

from egpcommon.egp_log import egp_logger


class TestEGPLogger(unittest.TestCase):
    """Test the EGP logger."""

    def test_egp_logger_creation(self) -> None:
        """Test the creation of an EGP logger."""
        logger = egp_logger("test_logger")
        self.assertIsInstance(logger, Logger)
        self.assertTrue(any(isinstance(handler, NullHandler) for handler in logger.handlers))
