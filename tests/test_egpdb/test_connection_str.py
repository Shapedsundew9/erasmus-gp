"""Tests for the connection_str_from_config function."""
import unittest
from os.path import dirname, join

from egpdb.common import connection_str_from_config
from egpdb.configuration import DatabaseConfig


class TestConnectionStrFromConfig(unittest.TestCase):
    """Test the connection_str_from_config function."""
    def setUp(self):
        self.db_config = DatabaseConfig(
            user="testuser",
            password=join(dirname(__file__), "data", "testpassword"),
            host="localhost",
            port=5432,
            dbname="testdb"
        )

    def test_connection_str_with_password(self):
        """Test the connection string with a password."""
        expected = "postgresql://testuser:testpassword@localhost:5432/testdb"
        result = connection_str_from_config(self.db_config, with_password=True)
        self.assertEqual(result, expected)

    def test_connection_str_without_password(self):
        """Test the connection string without a password."""
        expected = "postgresql://testuser@localhost:5432/testdb"
        result = connection_str_from_config(self.db_config, with_password=False)
        self.assertEqual(result, expected)
