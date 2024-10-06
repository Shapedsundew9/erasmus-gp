"""Tests for the text_token module."""

import unittest

from egppy.common.text_token import TextToken, register_token_code, token_library


class TestTextToken(unittest.TestCase):
    """Test the text_token module."""

    def setUp(self):
        # Clear the token library before each test
        token_library.clear()

    def test_register_token_valid(self):
        """Test that a valid token can be registered."""
        register_token_code("E00000", "A test token")
        self.assertIn("E00000", token_library)

    def test_register_token_invalid_prefix(self):
        """Test that an invalid token prefix cannot be registered."""
        with self.assertRaises(ValueError):
            register_token_code("N00000", "A test token")

    def test_register_token_invalid_length(self):
        """Test that an invalid token length cannot be registered."""
        with self.assertRaises(ValueError):
            register_token_code("E0000", "A test token")

    def test_register_token_invalid_number(self):
        """Test that an invalid token number cannot be registered."""
        with self.assertRaises(ValueError):
            register_token_code("E-2354", "A test token")

    def test_register_token_in_use(self):
        """Test that a token cannot be registered twice."""
        register_token_code("E00001", "A test token")
        with self.assertRaises(ValueError):
            register_token_code("E00001", "A test token")

    def test_text_token(self):
        """Test that a text_token can be created."""
        register_token_code("E00002", "A test token {test}")
        token = TextToken({"E00002": {"test": "test value"}})
        self.assertEqual(token.code, "E00002")
        self.assertEqual(token.parameters, {"test": "test value"})
        self.assertEqual(str(token), "E00002: A test token test value")


if __name__ == "__main__":
    unittest.main()
