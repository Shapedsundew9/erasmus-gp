"""Unit tests for table schema."""

import unittest
from logging import basicConfig, DEBUG
from os.path import abspath, dirname, join
from jsonschema import validate, ValidationError
from egppy.database.config.table_schema import read_table_schema, SCHEMA


basicConfig(
    level=DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s",
    filename="log/test.log"
)

class TestTableSchema(unittest.TestCase):
    """
    Test case for the TableSchema class.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.valid_table = {
            "table": "test",
            "schema": {
                "column1": {
                    "type": "int",
                    "nullable": False
                },
                "column2": {
                    "type": "varchar",
                    "nullable": True
                }
            }
        }
        self.invalid_table = {
            "name": "test",
            "database": "test_db",
            "schemas": "schema1.yaml"
        }
        self.test_file = join(dirname(abspath(__file__)), "data", "table_schema_valid.yaml")

    def test_read_table_valid(self):
        """
        Test reading a valid table file.
        """
        # Test reading a non-existent file
        read_table_schema(self.test_file)
        # No error

    def test_read_table_invalid(self):
        """
        Test reading a table file that does not exist.
        """
        with self.assertRaises(FileNotFoundError):
            read_table_schema("path/to/nonexistent/file.yaml")

    def test_validate_valid_table(self):
        """
        Test validating a valid table.
        """
        validate(self.valid_table, SCHEMA)
        # No error

    def test_validate_invalid_table(self):
        """
        Test validating an invalid table.
        """
        with self.assertRaises(ValidationError):
            validate(self.invalid_table, SCHEMA)


if __name__ == '__main__':
    unittest.main()
