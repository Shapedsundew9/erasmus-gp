"""Unit tests for the SQLAlchemy database module."""
import unittest

from egppy.database.sqlalchemy_db import SQLAlchemySqliteMem
from egppy.database.config.ds_config_schema import read_ds_config
from egppy.database.config.table_schema import read_table_schema


class TestSQLAlchemyDB(unittest.TestCase):
    """
    Test case for the SQLAlchemy database module.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.db_config = read_ds_config("tests/data/ds_config_valid.yaml")["database"]
        self.table_schema = read_table_schema("tests/data/table_schema_valid.yaml")

    def test_sqlalchemy_sqlite_mem(self):
        """
        Test the SQLAlchemySqliteMem class.
        """
        db = SQLAlchemySqliteMem(self.db_config)
        self.assertTrue(db.exists())
