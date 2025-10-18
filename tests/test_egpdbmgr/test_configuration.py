"""Tests for the configuration module."""

import tempfile
import unittest

from egpdb.configuration import DatabaseConfig
from egpdbmgr.configuration import DBManagerConfig


class TestDBManagerConfig(unittest.TestCase):
    """Test the DBManagerConfig class."""

    def setUp(self):
        self.default_config = {
            "name": "DBManagerConfig",
            "databases": {"erasmus_db": DatabaseConfig()},
            "managed_db": "erasmus_db",
            "managed_type": "pool",
            "upstream_dbs": [],
            "upstream_type": "library",
            "archive_db": "erasmus_archive_db",
        }

    def test_default_initialization(self):
        """Test the default initialization of the DBManagerConfig class."""
        config = DBManagerConfig()
        self.assertEqual(config.name, self.default_config["name"])
        self.assertEqual(config.databases, self.default_config["databases"])
        self.assertEqual(config.managed_db, self.default_config["managed_db"])
        self.assertEqual(config.managed_type, self.default_config["managed_type"])
        self.assertEqual(config.upstream_dbs, self.default_config["upstream_dbs"])
        self.assertEqual(config.upstream_type, self.default_config["upstream_type"])
        self.assertEqual(config.archive_db, self.default_config["archive_db"])

    def test_custom_initialization(self):
        """Test the custom initialization of the DBManagerConfig class."""
        custom_config = {
            "name": "CustomDBManagerConfig",
            "databases": {"custom_db": DatabaseConfig()},
            "managed_db": "custom_db",
            "managed_type": "library",
            "upstream_dbs": ["remote_db1", "remote_db2"],
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

    def test_to_json(self):
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

    def test_load_config(self):
        """Test the load_config method of the DBManagerConfig class."""
        config = DBManagerConfig()
        with tempfile.NamedTemporaryFile("w+", encoding="utf8", delete=True) as tmpfile:
            tmpfile.write(
                '{"name": "DBManagerConfig", "databases": {"erasmus_db": {}}, "managed_db": '
                '"erasmus_db", "managed_type": "pool", "upstream_dbs": [], "upstream_type": '
                '"library", "archive_db": "erasmus_archive_db"}'
            )
            tmpfile.flush()
            config.load_config(tmpfile.name)
        self.assertEqual(config.name, self.default_config["name"])
        self.assertEqual(config.databases, self.default_config["databases"])
        self.assertEqual(config.managed_db, self.default_config["managed_db"])
        self.assertEqual(config.managed_type, self.default_config["managed_type"])
        self.assertEqual(config.upstream_dbs, self.default_config["upstream_dbs"])
        self.assertEqual(config.upstream_type, self.default_config["upstream_type"])
        self.assertEqual(config.archive_db, self.default_config["archive_db"])

    def test_name_validation(self):
        """Test the validation of the name attribute."""
        config = DBManagerConfig()
        with self.assertRaises(ValueError):
            config.name = ""
        with self.assertRaises(ValueError):
            config.name = "a" * 65
        config.name = "ValidName"
        self.assertEqual(config.name, "ValidName")


if __name__ == "__main__":
    unittest.main()
