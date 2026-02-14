"""Tests for the egpdbmgr configuration module.

Tests cover DBManagerConfig initialization, property validation,
serialization (to_json), load/dump from signed JSON files,
cross-field verify() constraints, and TableTypes enum.
"""

import os
import tempfile
import unittest

from egpcommon.security import dump_signed_json
from egpdb.configuration import DatabaseConfig
from egpdbmgr.configuration import DBManagerConfig, TableTypes


class TestTableTypes(unittest.TestCase):
    """Test the TableTypes enum."""

    def test_values(self) -> None:
        """Test that all expected TableTypes values exist."""
        self.assertEqual(TableTypes.LOCAL, "local")
        self.assertEqual(TableTypes.POOL, "pool")
        self.assertEqual(TableTypes.LIBRARY, "library")
        self.assertEqual(TableTypes.ARCHIVE, "archive")

    def test_membership(self) -> None:
        """Test enum membership checks."""
        self.assertIn("local", TableTypes)
        self.assertIn("pool", TableTypes)
        self.assertNotIn("invalid", TableTypes)


class TestDBManagerConfig(unittest.TestCase):
    """Test the DBManagerConfig class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.default_config = {
            "name": "DBManagerConfig",
            "databases": {"erasmus_db": DatabaseConfig()},
            "managed_db": "erasmus_db",
            "managed_type": "pool",
            "upstream_dbs": [],
            "upstream_type": "library",
            "archive_db": "erasmus_archive_db",
        }

    def test_default_initialization(self) -> None:
        """Test the default initialization of the DBManagerConfig class."""
        config = DBManagerConfig()
        self.assertEqual(config.name, self.default_config["name"])
        self.assertEqual(config.databases, self.default_config["databases"])
        self.assertEqual(config.managed_db, self.default_config["managed_db"])
        self.assertEqual(config.managed_type, self.default_config["managed_type"])
        self.assertEqual(config.upstream_dbs, self.default_config["upstream_dbs"])
        self.assertEqual(config.upstream_type, self.default_config["upstream_type"])
        self.assertEqual(config.archive_db, self.default_config["archive_db"])
        self.assertIsNone(config.upstream_url)

    def test_custom_initialization(self) -> None:
        """Test the custom initialization of the DBManagerConfig class."""
        custom_config = {
            "name": "CustomDBManagerConfig",
            "databases": {"custom_db": DatabaseConfig()},
            "managed_db": "custom_db",
            "managed_type": "library",
            "upstream_dbs": [],
            "upstream_type": "archive",
            "archive_db": "custom_archive_db",
        }
        config = DBManagerConfig(
            name=custom_config["name"],
            databases=custom_config["databases"],
            managed_db=custom_config["managed_db"],
            managed_type=custom_config["managed_type"],
            upstream_dbs=custom_config["upstream_dbs"],
            upstream_type=custom_config["upstream_type"],
            archive_db=custom_config["archive_db"],
        )
        self.assertEqual(config.name, custom_config["name"])
        self.assertEqual(config.databases, custom_config["databases"])
        self.assertEqual(config.managed_db, custom_config["managed_db"])
        self.assertEqual(config.managed_type, custom_config["managed_type"])
        self.assertEqual(config.upstream_dbs, custom_config["upstream_dbs"])
        self.assertEqual(config.upstream_type, custom_config["upstream_type"])
        self.assertEqual(config.archive_db, custom_config["archive_db"])

    def test_initialization_with_dict_databases(self) -> None:
        """Test that databases can be initialized with plain dicts."""
        config = DBManagerConfig(databases={"test_db": {}}, managed_db="test_db")
        self.assertIsInstance(config.databases["test_db"], DatabaseConfig)

    # --- Property validation tests ---

    def test_name_validation_empty(self) -> None:
        """Test that empty name raises ValueError."""
        config = DBManagerConfig()
        with self.assertRaises(ValueError):
            config.name = ""

    def test_name_validation_too_long(self) -> None:
        """Test that name exceeding 64 chars raises ValueError."""
        config = DBManagerConfig()
        with self.assertRaises(ValueError):
            config.name = "a" * 65

    def test_name_validation_valid(self) -> None:
        """Test setting a valid name."""
        config = DBManagerConfig()
        config.name = "ValidName"
        self.assertEqual(config.name, "ValidName")

    def test_managed_db_validation_empty(self) -> None:
        """Test that empty managed_db raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(managed_db="")

    def test_managed_db_validation_too_long(self) -> None:
        """Test that managed_db exceeding 64 chars raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(managed_db="a" * 65)

    def test_archive_db_validation_empty(self) -> None:
        """Test that empty archive_db raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(archive_db="")

    def test_archive_db_validation_too_long(self) -> None:
        """Test that archive_db exceeding 64 chars raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(archive_db="a" * 65)

    def test_managed_type_validation(self) -> None:
        """Test that invalid managed_type raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(managed_type="invalid")

    def test_upstream_type_validation(self) -> None:
        """Test that invalid upstream_type raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(upstream_type="invalid")

    def test_databases_validation_not_dict(self) -> None:
        """Test that non-dict databases raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(databases="not_a_dict")

    def test_upstream_dbs_validation_not_list(self) -> None:
        """Test that non-list upstream_dbs raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(upstream_dbs="not_a_list")

    def test_upstream_url_validation_invalid(self) -> None:
        """Test that invalid upstream_url raises ValueError."""
        with self.assertRaises(ValueError):
            DBManagerConfig(upstream_url="not a url")

    def test_upstream_url_validation_none(self) -> None:
        """Test that None upstream_url is accepted."""
        config = DBManagerConfig(upstream_url=None)
        self.assertIsNone(config.upstream_url)

    # --- Cross-field verify() tests ---

    def test_verify_managed_db_not_in_databases(self) -> None:
        """Test that verify() raises ValueError when managed_db is not a databases key."""
        with self.assertRaises(ValueError, msg="managed_db 'nonexistent' must be a key"):
            DBManagerConfig(managed_db="nonexistent")

    def test_verify_upstream_dbs_not_in_databases(self) -> None:
        """Test that verify() raises ValueError when upstream_dbs entry is not a databases key."""
        with self.assertRaises(ValueError, msg="upstream_dbs entry"):
            DBManagerConfig(upstream_dbs=["nonexistent"])

    def test_verify_valid_upstream_dbs(self) -> None:
        """Test that verify() passes when upstream_dbs entries exist in databases."""
        config = DBManagerConfig(
            databases={"erasmus_db": DatabaseConfig(), "remote_db": DatabaseConfig()},
            upstream_dbs=["remote_db"],
        )
        self.assertEqual(config.upstream_dbs, ["remote_db"])

    # --- Serialization tests ---

    def test_to_json(self) -> None:
        """Test the to_json method of the DBManagerConfig class."""
        config = DBManagerConfig()
        expected_json = {
            "name": self.default_config["name"],
            "databases": {
                key: val.to_json() for key, val in self.default_config["databases"].items()
            },
            "managed_db": self.default_config["managed_db"],
            "managed_type": self.default_config["managed_type"],
            "upstream_dbs": self.default_config["upstream_dbs"],
            "upstream_type": self.default_config["upstream_type"],
            "archive_db": self.default_config["archive_db"],
        }
        self.assertEqual(config.to_json(), expected_json)

    def test_load_config(self) -> None:
        """Test the load_config method of the DBManagerConfig class."""
        config = DBManagerConfig()
        with tempfile.NamedTemporaryFile(
            "w+", encoding="utf8", delete=False, suffix=".json"
        ) as tmpfile:
            tmpfile_path = tmpfile.name

        try:
            test_data = {
                "name": "DBManagerConfig",
                "databases": {"erasmus_db": {}},
                "managed_db": "erasmus_db",
                "managed_type": "pool",
                "upstream_dbs": [],
                "upstream_type": "library",
                "archive_db": "erasmus_archive_db",
            }
            dump_signed_json(test_data, tmpfile_path)
            config.load_config(tmpfile_path)

            self.assertEqual(config.name, self.default_config["name"])
            self.assertEqual(config.databases, self.default_config["databases"])
            self.assertEqual(config.managed_db, self.default_config["managed_db"])
            self.assertEqual(config.managed_type, self.default_config["managed_type"])
            self.assertEqual(config.upstream_dbs, self.default_config["upstream_dbs"])
            self.assertEqual(config.upstream_type, self.default_config["upstream_type"])
            self.assertEqual(config.archive_db, self.default_config["archive_db"])
        finally:
            if os.path.exists(tmpfile_path):
                os.unlink(tmpfile_path)
            if os.path.exists(f"{tmpfile_path}.sig"):
                os.unlink(f"{tmpfile_path}.sig")

    # --- __slots__ test ---

    def test_slots_defined(self) -> None:
        """Test that __slots__ is defined on DBManagerConfig."""
        self.assertIn("_name", DBManagerConfig.__slots__)
        self.assertIn("_databases", DBManagerConfig.__slots__)
        self.assertIn("_managed_db", DBManagerConfig.__slots__)
        self.assertIn("_managed_type", DBManagerConfig.__slots__)
        self.assertIn("_upstream_dbs", DBManagerConfig.__slots__)
        self.assertIn("_upstream_type", DBManagerConfig.__slots__)
        self.assertIn("_upstream_url", DBManagerConfig.__slots__)
        self.assertIn("_archive_db", DBManagerConfig.__slots__)


if __name__ == "__main__":
    unittest.main()
