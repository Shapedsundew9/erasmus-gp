"""Unit tests for the sqlite table module."""
import unittest
from egppy.database.sqlalchemy_db import SQLAlchemySqliteMem
from egppy.database.sqlite_table import SQLiteTable
from egppy.database.config.table_schema import read_table_schema
from egppy.database.config.ds_config_schema import read_ds_config


class TestSQLiteTable(unittest.TestCase):
    """
    Test case for the SQLite table module.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.table_schema = read_table_schema("tests/data/table_schema_valid.yaml")
        self.db_config = read_ds_config("tests/data/ds_config_valid.yaml")["database"]

    def test_sqlite_table_exists(self):
        """
        Test the SQLiteTable class.
        """
        table = SQLiteTable(self.table_schema, SQLAlchemySqliteMem(self.db_config))
        self.assertTrue(table.exists())
