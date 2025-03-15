"""Tests for the Properties module."""

import unittest

from egpcommon.properties import PropertiesBD

class TestProperties(unittest.TestCase):
    """Test the Properties."""

    def test_properties(self) -> None:
        """Test the creation of a Properties instance."""
        properties_instance = PropertiesBD(0x0)
        self.assertIsInstance(properties_instance, PropertiesBD)
