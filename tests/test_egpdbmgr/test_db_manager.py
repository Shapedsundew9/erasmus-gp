"""Tests for the egpdbmgr db_manager module.

Tests cover module-level constants (GC_TABLE_CONVERSIONS, META_TABLE_SCHEMA,
SOURCES_TABLE_SCHEMA), the DBManager class initialization, table creation,
and schema preparation.
"""

from unittest import TestCase

from egpdb.configuration import ColumnSchema, DatabaseConfig
from egpdb.database import db_delete
from egpdbmgr.configuration import DBManagerConfig, TableTypes
from egpdbmgr.db_manager import (
    GC_TABLE_CONVERSIONS,
    META_TABLE_SCHEMA,
    SOURCES_TABLE_SCHEMA,
    DBManager,
)

# Unique DB name to avoid conflicts with other test modules
_TEST_DB_NAME = "test_egpdbmgr_db"
_TEST_DB_CONFIG = DatabaseConfig(dbname=_TEST_DB_NAME, host="postgres")


class TestModuleConstants(TestCase):
    """Test module-level constants in db_manager.py."""

    def test_gc_table_conversions_is_tuple(self) -> None:
        """Test that GC_TABLE_CONVERSIONS is a tuple of 3-tuples."""
        self.assertIsInstance(GC_TABLE_CONVERSIONS, tuple)
        for entry in GC_TABLE_CONVERSIONS:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 3, f"Conversion entry {entry} must have 3 elements")
            self.assertIsInstance(entry[0], str, f"First element of {entry} must be a str")

    def test_gc_table_conversions_has_cgraph(self) -> None:
        """Test that GC_TABLE_CONVERSIONS includes cgraph conversion."""
        names = [c[0] for c in GC_TABLE_CONVERSIONS]
        self.assertIn("cgraph", names)

    def test_gc_table_conversions_has_properties(self) -> None:
        """Test that GC_TABLE_CONVERSIONS includes properties conversion."""
        names = [c[0] for c in GC_TABLE_CONVERSIONS]
        self.assertIn("properties", names)

    def test_meta_table_schema_keys(self) -> None:
        """Test that META_TABLE_SCHEMA has the expected keys."""
        self.assertIn("created", META_TABLE_SCHEMA)
        self.assertIn("creator", META_TABLE_SCHEMA)

    def test_meta_table_schema_values_are_column_schema(self) -> None:
        """Test that META_TABLE_SCHEMA values are ColumnSchema instances."""
        for key, val in META_TABLE_SCHEMA.items():
            self.assertIsInstance(val, ColumnSchema, f"META_TABLE_SCHEMA['{key}'] type")

    def test_sources_table_schema_keys(self) -> None:
        """Test that SOURCES_TABLE_SCHEMA has the expected keys."""
        expected_keys = {
            "source_path",
            "creator_uuid",
            "timestamp",
            "file_hash",
            "signature",
            "algorithm",
        }
        self.assertEqual(set(SOURCES_TABLE_SCHEMA.keys()), expected_keys)

    def test_sources_table_schema_values_are_column_schema(self) -> None:
        """Test that SOURCES_TABLE_SCHEMA values are ColumnSchema instances."""
        for key, val in SOURCES_TABLE_SCHEMA.items():
            self.assertIsInstance(val, ColumnSchema, f"SOURCES_TABLE_SCHEMA['{key}'] type")


class TestDBManagerPrepareSchemas(TestCase):
    """Test the DBManager.prepare_schemas method.

    Uses a real PostgreSQL connection to create the DBManager, then tests
    the schema preparation logic.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Create a DBManager for testing."""
        config = DBManagerConfig(
            name="TestDBManager",
            databases={_TEST_DB_NAME: _TEST_DB_CONFIG},
            managed_db=_TEST_DB_NAME,
            managed_type=TableTypes.POOL,
        )
        cls.db_manager = DBManager(config, delete=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the test database."""
        db_delete(_TEST_DB_NAME, _TEST_DB_CONFIG)

    def test_prepare_schemas_returns_all_table_types(self) -> None:
        """Test that prepare_schemas returns a dict with all TableTypes as keys."""
        schemas = self.db_manager.prepare_schemas()
        for table_type in TableTypes:
            self.assertIn(table_type, schemas, f"Missing schema for {table_type}")

    def test_prepare_schemas_not_empty(self) -> None:
        """Test that each schema in prepare_schemas is a non-empty dict."""
        schemas = self.db_manager.prepare_schemas()
        for table_type, schema in schemas.items():
            self.assertIsInstance(schema, dict, f"Schema for {table_type} must be dict")
            self.assertGreater(len(schema), 0, f"Schema for {table_type} must not be empty")

    def test_managed_gc_table_created(self) -> None:
        """Test that the managed GC table was created."""
        self.assertIsNotNone(self.db_manager.managed_gc_table)

    def test_managed_meta_table_created(self) -> None:
        """Test that the managed meta table was created."""
        self.assertIsNotNone(self.db_manager.managed_gc_meta_table)

    def test_managed_sources_table_created(self) -> None:
        """Test that the managed sources table was created."""
        self.assertIsNotNone(self.db_manager.managed_sources_table)

    def test_config_stored(self) -> None:
        """Test that the config is stored on the DBManager."""
        self.assertIsInstance(self.db_manager.config, DBManagerConfig)
        self.assertEqual(self.db_manager.config.name, "TestDBManager")

    def test_operations_does_not_raise(self) -> None:
        """Test that operations() runs without raising."""
        self.db_manager.operations()
