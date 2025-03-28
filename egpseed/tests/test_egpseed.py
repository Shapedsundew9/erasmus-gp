"""Test the generate module."""

import unittest
from egpseed.egpseed.generate import generate_codons



class TestGenerateCodons(unittest.TestCase):
    """Test the generate_codons function."""

    def test_generate_codons(self):
        """Test that generate_codons completes without raising an exception."""
        generate_codons()


if __name__ == "__main__":
    unittest.main()
