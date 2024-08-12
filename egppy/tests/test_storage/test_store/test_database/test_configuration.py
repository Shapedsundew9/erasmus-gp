"""Test the database configuration class."""
from unittest import TestCase
from egppy.storage.store.database.configuration import DatabaseConfig


class TestDatabaseConfig(TestCase):
    """Test the database configuration class."""

    def test_init(self):
        """Test the initialization of the class."""
        config = DatabaseConfig()
        self.assertEqual(config.dbname, "postgres")
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.password, "Password123!")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.maintenance_db, "postgres")
        self.assertEqual(config.retires, 3)
        self.assertEqual(config.user, "postgres")

    def test_dbname(self):
        """Test the dbname property."""
        config = DatabaseConfig()
        config.dbname = "postgres"
        self.assertEqual(config.dbname, "postgres")
        with self.assertRaises(AssertionError):
            config.dbname = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.dbname = "_postgres"
        with self.assertRaises(AssertionError):
            config.dbname = "a"*257

    def test_host(self):
        """Test the host property."""
        config = DatabaseConfig()
        config.host = "localhost.com"
        self.assertEqual(config.host, "localhost.com")
        with self.assertRaises(AssertionError):
            config.host = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.host = "localhost.com_"
        with self.assertRaises(AssertionError):
            config.host = "a"*257

    def test_password(self):
        """Test the password property."""
        config = DatabaseConfig()
        config.password = "Password1!"
        self.assertEqual(config.password, "Password1!")
        with self.assertRaises(AssertionError):
            config.password = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.password = "pass"
        with self.assertRaises(AssertionError):
            config.password = "a"*257

    def test_port(self):
        """Test the port property."""
        config = DatabaseConfig()
        config.port = 5432
        self.assertEqual(config.port, 5432)
        with self.assertRaises(AssertionError):
            config.port = "5432"  # type: ignore
        with self.assertRaises(AssertionError):
            config.port = 0

    def test_maintenance_db(self):
        """Test the maintenance_db property."""
        config = DatabaseConfig()
        config.maintenance_db = "postgres"
        self.assertEqual(config.maintenance_db, "postgres")
        with self.assertRaises(AssertionError):
            config.maintenance_db = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.maintenance_db = "_postgres"
        with self.assertRaises(AssertionError):
            config.maintenance_db = "a"*257

    def test_retires(self):
        """Test the retires property."""
        config = DatabaseConfig()
        config.retires = 4
        self.assertEqual(config.retires, 4)
        with self.assertRaises(AssertionError):
            config.retires = "3"  # type: ignore
        with self.assertRaises(AssertionError):
            config.retires = 0

    def test_user(self):
        """Test the user property."""
        config = DatabaseConfig()
        # file deepcode ignore NoHardcodedCredentials/test: Unit test
        config.user = "postgres"  #
        self.assertEqual(config.user, "postgres")
        with self.assertRaises(AssertionError):
            config.user = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.user = "_postgres"
        with self.assertRaises(AssertionError):
            config.user = "a"*257

    def test_accessors(self):
        """Test the accessors."""
        config = DatabaseConfig()
        config["dbname"] = "fred"
        config["host"] = "127.0.0.1"
        config["password"] = "A1b2C3d4E5!"
        config["port"] = 5433
        config["maintenance_db"] = "mdb"
        config["retires"] = 8
        config["user"] = "brian"
        self.assertEqual(config["dbname"], "fred")
        self.assertEqual(config["host"], "127.0.0.1")
        self.assertEqual(config["password"], "A1b2C3d4E5!")
        self.assertEqual(config["port"], 5433)
        self.assertEqual(config["maintenance_db"], "mdb")
        self.assertEqual(config["retires"], 8)
        self.assertEqual(config["user"], "brian")

    def test_to_json(self):
        """Test the to_json method."""
        config = DatabaseConfig()
        config["dbname"] = "fred"
        config["host"] = "127.0.0.1"
        config["password"] = "A1b2C3d4E5!"
        config["port"] = 5433
        config["maintenance_db"] = "mdb"
        config["retires"] = 8
        config["user"] = "brian"
        dict_config = {
            "dbname": "fred",
            "host": "127.0.0.1",
            # file deepcode ignore NoHardcodedPasswords/test: Unit test
            "password": "A1b2C3d4E5!",
            "port": 5433,
            "maintenance_db": "mdb",
            "retires": 8,
            "user": "brian"
        }
        self.assertEqual(config.to_json(), dict_config)
