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
            "local_db": "erasmus_db",
            "local_type": "pool",
            "remote_dbs": [],
            "remote_type": "library",
            "archive_db": "erasmus_archive_db",
        }

    def test_default_initialization(self):
        """Test the default initialization of the DBManagerConfig class."""
        config = DBManagerConfig()
        self.assertEqual(config.name, self.default_config["name"])
        self.assertEqual(config.databases, self.default_config["databases"])
        self.assertEqual(config.local_db, self.default_config["local_db"])
        self.assertEqual(config.local_type, self.default_config["local_type"])
        self.assertEqual(config.remote_dbs, self.default_config["remote_dbs"])
        self.assertEqual(config.remote_type, self.default_config["remote_type"])
        self.assertEqual(config.archive_db, self.default_config["archive_db"])

    def test_custom_initialization(self):
        """Test the custom initialization of the DBManagerConfig class."""
        custom_config = {
            "name": "CustomDBManagerConfig",
            "databases": {"custom_db": DatabaseConfig()},
            "local_db": "custom_db",
            "local_type": "library",
            "remote_dbs": ["remote_db1", "remote_db2"],
            "remote_type": "archive",
            "archive_db": "custom_archive_db",
        }
        config = DBManagerConfig(
            name=custom_config["name"],
            databases=custom_config["databases"],
            local_db=custom_config["local_db"],
            local_type=custom_config["local_type"],
            remote_dbs=custom_config["remote_dbs"],
            remote_type=custom_config["remote_type"],
            archive_db=custom_config["archive_db"],
        )
        self.assertEqual(config.name, custom_config["name"])
        self.assertEqual(config.databases, custom_config["databases"])
        self.assertEqual(config.local_db, custom_config["local_db"])
        self.assertEqual(config.local_type, custom_config["local_type"])
        self.assertEqual(config.remote_dbs, custom_config["remote_dbs"])
        self.assertEqual(config.remote_type, custom_config["remote_type"])
        self.assertEqual(config.archive_db, custom_config["archive_db"])

    def test_to_json(self):
        """Test the to_json method of the DBManagerConfig class."""
        config = DBManagerConfig()
        expected_json = {
            "name": self.default_config["name"],
            "databases": {
                key: val.to_json() for key, val in self.default_config["databases"].items()
            },
            "local_db": self.default_config["local_db"],
            "local_type": self.default_config["local_type"],
            "remote_dbs": self.default_config["remote_dbs"],
            "remote_type": self.default_config["remote_type"],
            "archive_db": self.default_config["archive_db"],
        }
        self.assertEqual(config.to_json(), expected_json)

    def test_load_config(self):
        """Test the load_config method of the DBManagerConfig class."""
        config = DBManagerConfig()
        with tempfile.NamedTemporaryFile("w+", encoding="utf8", delete=True) as tmpfile:
            tmpfile.write(
                '{"name": "DBManagerConfig", "databases": {"erasmus_db": {}}, "local_db": '
                '"erasmus_db", "local_type": "pool", "remote_dbs": [], "remote_type": '
                '"library", "archive_db": "erasmus_archive_db"}'
            )
            tmpfile.flush()
            config.load_config(tmpfile.name)
        self.assertEqual(config.name, self.default_config["name"])
        self.assertEqual(config.databases, self.default_config["databases"])
        self.assertEqual(config.local_db, self.default_config["local_db"])
        self.assertEqual(config.local_type, self.default_config["local_type"])
        self.assertEqual(config.remote_dbs, self.default_config["remote_dbs"])
        self.assertEqual(config.remote_type, self.default_config["remote_type"])
        self.assertEqual(config.archive_db, self.default_config["archive_db"])

    def test_name_validation(self):
        """Test the validation of the name attribute."""
        config = DBManagerConfig()
        with self.assertRaises(AssertionError):
            config.name = ""
        with self.assertRaises(AssertionError):
            config.name = "a" * 65
        config.name = "ValidName"
        self.assertEqual(config.name, "ValidName")


if __name__ == "__main__":
    unittest.main()
