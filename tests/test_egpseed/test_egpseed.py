"""Test the generate module."""

import unittest
from egpseed.generate_codons import generate_codons


class TestGenerateCodons(unittest.TestCase):
    """Test the generate_codons function."""

    def test_generate_codons(self) -> None:
        """Test that generate_codons completes without raising an exception."""
        generate_codons()
