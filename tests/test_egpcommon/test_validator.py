"""Unit tests for the Validator class."""

import unittest
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from egpcommon.validator import Validator


# pylint: disable=protected-access
class TestValidator(unittest.TestCase):
    """Test cases for the Validator class."""

    def setUp(self):
        """Set up the test case."""
        self.validator = Validator()
        self.patcher = patch("egpcommon.validator._logger")
        self.mock_logger = self.patcher.start()
        self.mock_logger.isEnabledFor.return_value = True
        self.addCleanup(self.patcher.stop)

    def test_in_range(self):
        """Test the _in_range method."""
        self.assertTrue(self.validator._in_range("attr", 5, 0, 10))
        self.assertFalse(self.validator._in_range("attr", 15, 0, 10))

    def test_is_bool(self):
        """Test the _is_bool method."""
        self.assertTrue(self.validator._is_bool("attr", True))
        self.assertFalse(self.validator._is_bool("attr", "not a bool"))

    def test_is_bytes(self):
        """Test the _is_bytes method."""
        self.assertTrue(self.validator._is_bytes("attr", b"some bytes"))
        self.assertFalse(self.validator._is_bytes("attr", "not bytes"))

    def test_is_callable(self):
        """Test the _is_callable method."""
        self.assertTrue(self.validator._is_callable("attr", lambda: None))
        self.assertFalse(self.validator._is_callable("attr", "not callable"))

    def test_is_datetime(self):
        """Test the _is_datetime method."""
        self.assertTrue(self.validator._is_datetime("attr", datetime.now()))
        self.assertFalse(self.validator._is_datetime("attr", "not a datetime"))

    def test_is_dict(self):
        """Test the _is_dict method."""
        self.assertTrue(self.validator._is_dict("attr", {"key": "value"}))
        self.assertFalse(self.validator._is_dict("attr", "not a dict"))

    def test_is_float(self):
        """Test the _is_float method."""
        self.assertTrue(self.validator._is_float("attr", 1.23))
        self.assertFalse(self.validator._is_float("attr", 123))

    def test_is_int(self):
        """Test the _is_int method."""
        self.assertTrue(self.validator._is_int("attr", 123))
        self.assertFalse(self.validator._is_int("attr", 1.23))

    def test_is_list(self):
        """Test the _is_list method."""
        self.assertTrue(self.validator._is_list("attr", [1, 2, 3]))
        self.assertFalse(self.validator._is_list("attr", "not a list"))

    def test_is_string(self):
        """Test the _is_string method."""
        self.assertTrue(self.validator._is_string("attr", "a string"))
        self.assertFalse(self.validator._is_string("attr", 123))

    def test_is_tuple(self):
        """Test the _is_tuple method."""
        self.assertTrue(self.validator._is_tuple("attr", (1, 2, 3)))
        self.assertFalse(self.validator._is_tuple("attr", [1, 2, 3]))

    def test_is_uuid(self):
        """Test the _is_uuid method."""
        self.assertTrue(self.validator._is_uuid("attr", uuid4()))
        self.assertFalse(self.validator._is_uuid("attr", "not a uuid"))

    def test_is_hostname(self):
        """Test the _is_hostname method."""
        self.assertTrue(self.validator._is_hostname("attr", "example.com"))
        self.assertTrue(self.validator._is_hostname("attr", "sub.example.co.uk"))
        self.assertFalse(self.validator._is_hostname("attr", "-invalid.com"))
        self.assertFalse(self.validator._is_hostname("attr", "invalid-.com"))
        self.assertFalse(self.validator._is_hostname("attr", "a" * 64 + ".com"))

    def test_is_ip(self):
        """Test the _is_ip method."""
        self.assertTrue(self.validator._is_ip("attr", "192.168.1.1"))
        self.assertTrue(self.validator._is_ip("attr", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
        self.assertFalse(self.validator._is_ip("attr", "not an ip"))

    def test_is_ip_or_hostname(self):
        """Test the _is_ip_or_hostname method."""
        self.assertTrue(self.validator._is_ip_or_hostname("attr", "192.168.1.1"))
        self.assertTrue(self.validator._is_ip_or_hostname("attr", "example.com"))
        self.assertFalse(self.validator._is_ip_or_hostname("attr", "not valid"))


if __name__ == "__main__":
    unittest.main()
