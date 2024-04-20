"""Unit tests for the datastore_schema module."""

import unittest
from os.path import abspath, dirname, join
from jsonschema import ValidationError, validate
from egppy.database.config.ds_config_schema import read_ds_config, SCHEMA


class TestDSConfigSchema(unittest.TestCase):
    """
    Test case for the DatastoreConfigSchema class.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.valid_ds_config = {
            "name": "test",
            "database": {"dbname": "test_db"},
            "schemas": ["schema1/a.yaml", "/root/schema2/b.yaml"]
        }
        self.invalid_ds_config = {
            "name": "test",
            "database": "test_db",
            "schemas": "schema1.yaml"
        }
        self.test_file = join(dirname(abspath(__file__)), "data", "ds_config_valid.yaml")

    def test_read_ds_config_valid(self):
        """
        Test reading a valid datastore file.
        """
        # Test reading a non-existent file
        with self.assertRaises(FileNotFoundError):
            read_ds_config("path/to/nonexistent/file.yaml")

    def test_read_ds_config_invalid(self):
        """
        Test reading a datastore file that does not exist.
        """
        with self.assertRaises(FileNotFoundError):
            read_ds_config("path/to/nonexistent/file.yaml")

    def test_validate_valid_ds_config(self):
        """
        Test validating a valid datastore.
        """
        validate(self.valid_ds_config, SCHEMA)
        # No error

    def test_validate_invalid_ds_config(self):
        """
        Test validating an invalid datastore.
        """
        with self.assertRaises(ValidationError):
            validate(self.invalid_ds_config, SCHEMA)


if __name__ == '__main__':
    unittest.main()
