"""Test the database configuration class."""

from os.path import dirname, expanduser, join, normpath
from unittest import TestCase

from egpdb.configuration import ColumnSchema, DatabaseConfig, TableConfig

# Location of the password file
PSWD_FILE = join(dirname(__file__), "data", "db_password")


class TestDatabaseConfig(TestCase):
    """Test the database configuration class."""

    def test_init(self):
        """Test the initialization of the class."""
        config = DatabaseConfig(password=PSWD_FILE)
        self.assertEqual(config.dbname, "erasmus_db")
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.maintenance_db, "postgres")
        self.assertEqual(config.retries, 3)
        self.assertEqual(config.user, "postgres")

    def test_dbname(self):
        """Test the dbname property."""
        config = DatabaseConfig(password=PSWD_FILE)
        config.dbname = "postgres"
        self.assertEqual(config.dbname, "postgres")
        with self.assertRaises(AssertionError):
            config.dbname = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.dbname = "_postgres"
        with self.assertRaises(AssertionError):
            config.dbname = "a" * 257

    def test_host(self):
        """Test the host property."""
        config = DatabaseConfig(password=PSWD_FILE)
        config.host = "localhost.com"
        self.assertEqual(config.host, "localhost.com")
        with self.assertRaises(AssertionError):
            config.host = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.host = "localhost.com_"
        with self.assertRaises(AssertionError):
            config.host = "a" * 257

    def test_port(self):
        """Test the port property."""
        config = DatabaseConfig(password=PSWD_FILE)
        config.port = 5432
        self.assertEqual(config.port, 5432)
        with self.assertRaises(AssertionError):
            config.port = "5432"  # type: ignore
        with self.assertRaises(AssertionError):
            config.port = 0

    def test_maintenance_db(self):
        """Test the maintenance_db property."""
        config = DatabaseConfig(password=PSWD_FILE)
        config.maintenance_db = "postgres"
        self.assertEqual(config.maintenance_db, "postgres")
        with self.assertRaises(AssertionError):
            config.maintenance_db = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.maintenance_db = "_postgres"
        with self.assertRaises(AssertionError):
            config.maintenance_db = "a" * 257

    def test_retires(self):
        """Test the retires property."""
        config = DatabaseConfig(password=PSWD_FILE)
        config.retries = 4
        self.assertEqual(config.retries, 4)
        with self.assertRaises(AssertionError):
            config.retries = "3"  # type: ignore
        with self.assertRaises(AssertionError):
            config.retries = 0

    def test_user(self):
        """Test the user property."""
        config = DatabaseConfig(password=PSWD_FILE)
        # file deepcode ignore NoHardcodedCredentials/test: Unit test
        config.user = "postgres"  #
        self.assertEqual(config.user, "postgres")
        with self.assertRaises(AssertionError):
            config.user = 1  # type: ignore
        with self.assertRaises(AssertionError):
            config.user = "_postgres"
        with self.assertRaises(AssertionError):
            config.user = "a" * 257

    def test_accessors(self):
        """Test the accessors."""
        config = DatabaseConfig(password=PSWD_FILE)
        config["dbname"] = "fred"
        config["host"] = "127.0.0.1"
        config["port"] = 5433
        config["maintenance_db"] = "mdb"
        config["retries"] = 8
        config["user"] = "brian"
        self.assertEqual(config["dbname"], "fred")
        self.assertEqual(config["host"], "127.0.0.1")
        self.assertEqual(config["port"], 5433)
        self.assertEqual(config["password"], "abcdefghij")
        self.assertEqual(config["maintenance_db"], "mdb")
        self.assertEqual(config["retries"], 8)
        self.assertEqual(config["user"], "brian")

    def test_to_json(self):
        """Test the to_json method."""
        config = DatabaseConfig(password=PSWD_FILE)
        config["dbname"] = "fred"
        config["host"] = "127.0.0.1"
        config["port"] = 5433
        config["maintenance_db"] = "mdb"
        config["retries"] = 8
        config["user"] = "brian"
        dict_config = {
            "dbname": "fred",
            "host": "127.0.0.1",
            "port": 5433,
            # deepcode ignore NoHardcodedPasswords/test: Unit test
            "password": PSWD_FILE,
            "maintenance_db": "mdb",
            "retries": 8,
            "user": "brian",
        }
        self.assertEqual(config.to_json(), dict_config)

    def test_invalid_password(self):
        """Test the password property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.password = 123  # type: ignore
        with self.assertRaises(AssertionError):
            config.password = ""

    def test_invalid_dbname(self):
        """Test the dbname property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.dbname = "1invalid_dbname"
        with self.assertRaises(AssertionError):
            config.dbname = "invalid_dbname_with_special_characters!@#"

    def test_invalid_host(self):
        """Test the host property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.host = "invalid_host_with_special_characters!@#"
        with self.assertRaises(AssertionError):
            config.host = ""

    def test_invalid_port(self):
        """Test the port property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.port = -1
        with self.assertRaises(AssertionError):
            config.port = 70000

    def test_invalid_maintenance_db(self):
        """Test the maintenance_db property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.maintenance_db = "1invalid_dbname"
        with self.assertRaises(AssertionError):
            config.maintenance_db = "invalid_dbname_with_special_characters!@#"

    def test_invalid_retries(self):
        """Test the retries property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.retries = -1
        with self.assertRaises(AssertionError):
            config.retries = 0

    def test_invalid_user(self):
        """Test the user property with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.user = "1invalid_user"
        with self.assertRaises(AssertionError):
            config.user = "invalid_user_with_special_characters!@#"

    def test_password(self):
        """Test the password property."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config.password = 123  # type: ignore
        with self.assertRaises(AssertionError):
            config.password = ""

    def test_invalid_accessors(self):
        """Test the accessors with invalid values."""
        config = DatabaseConfig(password=PSWD_FILE)
        with self.assertRaises(AssertionError):
            config["dbname"] = 123  # type: ignore
        with self.assertRaises(AssertionError):
            config["host"] = 123  # type: ignore
        with self.assertRaises(AssertionError):
            config["port"] = "invalid_port"  # type: ignore
        with self.assertRaises(AssertionError):
            config["maintenance_db"] = 123  # type: ignore
        with self.assertRaises(AssertionError):
            config["retries"] = "invalid_retries"  # type: ignore
        with self.assertRaises(AssertionError):
            config["user"] = 123  # type: ignore


class TestColumnSchema(TestCase):
    """Test the column schema class."""

    def test_init(self):
        """Test the initialization of the class."""
        schema = ColumnSchema(
            db_type="VARCHAR",
            default="default_value",
            description="A column",
            nullable=False,
            primary_key=True,
            index=None,
            unique=True,
        )
        self.assertEqual(schema.db_type, "VARCHAR")
        self.assertEqual(schema.default, "default_value")
        self.assertEqual(schema.description, "A column")
        self.assertFalse(schema.nullable)
        self.assertTrue(schema.primary_key)
        self.assertIsNone(schema.index)
        self.assertTrue(schema.unique)

    def test_db_type(self):
        """Test the db_type property."""
        schema = ColumnSchema()
        schema.db_type = "INTEGER"
        self.assertEqual(schema.db_type, "INTEGER")
        with self.assertRaises(AssertionError):
            schema.db_type = 123  # type: ignore

    def test_volatile(self):
        """Test the volatile property."""
        schema = ColumnSchema()
        schema.volatile = True
        self.assertTrue(schema.volatile)
        with self.assertRaises(AssertionError):
            schema.volatile = "True"  # type: ignore

    def test_default(self):
        """Test the default property."""
        schema = ColumnSchema()
        schema.default = "default_value"
        self.assertEqual(schema.default, "default_value")
        with self.assertRaises(AssertionError):
            schema.default = 123  # type: ignore

    def test_description(self):
        """Test the description property."""
        schema = ColumnSchema()
        schema.description = "A column"
        self.assertEqual(schema.description, "A column")
        with self.assertRaises(AssertionError):
            schema.description = 123  # type: ignore

    def test_nullable(self):
        """Test the nullable property."""
        schema = ColumnSchema()
        schema.nullable = True
        self.assertTrue(schema.nullable)
        with self.assertRaises(AssertionError):
            schema.nullable = "True"  # type: ignore

    def test_primary_key(self):
        """Test the primary_key property."""
        schema = ColumnSchema()
        schema.primary_key = True
        self.assertTrue(schema.primary_key)
        with self.assertRaises(AssertionError):
            schema.primary_key = "True"  # type: ignore

    def test_index(self):
        """Test the index property."""
        schema = ColumnSchema()
        schema.index = "btree"
        self.assertEqual(schema.index, "btree")
        with self.assertRaises(AssertionError):
            schema.index = 123  # type: ignore

    def test_unique(self):
        """Test the unique property."""
        schema = ColumnSchema()
        schema.unique = True
        self.assertTrue(schema.unique)
        with self.assertRaises(AssertionError):
            schema.unique = "True"  # type: ignore

    def test_to_json(self):
        """Test the to_json method."""
        schema = ColumnSchema(
            db_type="VARCHAR",
            default="default_value",
            description="A column",
            nullable=True,
            primary_key=False,
            index="btree",
            unique=False,
        )
        dict_schema = {
            "db_type": "VARCHAR",
            "volatile": False,
            "default": "default_value",
            "description": "A column",
            "nullable": True,
            "primary_key": False,
            "index": "btree",
            "unique": False,
        }
        self.assertEqual(schema.to_json(), dict_schema)

    def test_primary_key_consistency(self):
        """Test the consistency method for primary key."""
        with self.assertRaises(ValueError):
            ColumnSchema(primary_key=True, nullable=True)
        # Unique will be forced to True
        config = ColumnSchema(primary_key=True, unique=False)
        with self.assertRaises(RuntimeError):
            # However, this will raise an error
            config.unique = False
            config.consistency()

    def test_index_consistency(self):
        """Test the consistency method for index."""
        with self.assertRaises(ValueError):
            ColumnSchema(primary_key=True, index="btree")
        with self.assertRaises(ValueError):
            ColumnSchema(unique=True, index="btree")


class TestTableConfig(TestCase):
    """Test the table configuration class."""

    def test_init(self):
        """Test the initialization of the class."""
        config = TableConfig()
        self.assertIsInstance(config.database, DatabaseConfig)
        self.assertEqual(config.table, "default_table")
        self.assertEqual(config.schema, {})
        self.assertEqual(config.ptr_map, {})
        self.assertEqual(config.data_file_folder, ".")
        self.assertEqual(config.data_files, [])
        self.assertFalse(config.delete_db)
        self.assertFalse(config.delete_table)
        self.assertFalse(config.create_db)
        self.assertFalse(config.create_table)
        self.assertFalse(config.wait_for_db)
        self.assertFalse(config.wait_for_table)
        self.assertEqual(config.conversions, tuple())

    def test_table(self):
        """Test the table property."""
        config = TableConfig()
        config.table = "new_table"
        self.assertEqual(config.table, "new_table")
        with self.assertRaises(AssertionError):
            config.table = 123  # type: ignore

    def test_schema(self):
        """Test the schema property."""
        config = TableConfig()
        schema = {"column1": ColumnSchema(db_type="INTEGER")}
        config.schema = schema
        self.assertEqual(config.schema["column1"].db_type, "INTEGER")
        with self.assertRaises(AssertionError):
            config.schema = "invalid_schema"  # type: ignore

    def test_ptr_map(self):
        """Test the ptr_map property."""
        config = TableConfig()
        ptr_map = {"column1": "column2"}
        config.ptr_map = ptr_map
        self.assertEqual(config.ptr_map["column1"], "column2")
        with self.assertRaises(AssertionError):
            config.ptr_map = "invalid_ptr_map"  # type: ignore

    def test_data_file_folder(self):
        """Test the data_file_folder property."""
        config = TableConfig()
        config.data_file_folder = "~/data"
        self.assertEqual(config.data_file_folder,
                         normpath(expanduser("~/data")))
        with self.assertRaises(AssertionError):
            config.data_file_folder = 123  # type: ignore

    def test_data_files(self):
        """Test the data_files property."""
        config = TableConfig()
        data_files = ["file1.csv", "file2.csv"]
        config.data_files = data_files
        self.assertEqual(config.data_files, data_files)
        with self.assertRaises(AssertionError):
            config.data_files = "invalid_data_files"  # type: ignore

    def test_delete_db(self):
        """Test the delete_db property."""
        config = TableConfig()
        config.delete_db = True
        self.assertTrue(config.delete_db)
        with self.assertRaises(AssertionError):
            config.delete_db = "invalid_delete_db"  # type: ignore

    def test_delete_table(self):
        """Test the delete_table property."""
        config = TableConfig()
        config.delete_table = True
        self.assertTrue(config.delete_table)
        with self.assertRaises(AssertionError):
            config.delete_table = "invalid_delete_table"  # type: ignore

    def test_create_db(self):
        """Test the create_db property."""
        config = TableConfig()
        config.create_db = True
        self.assertTrue(config.create_db)
        with self.assertRaises(AssertionError):
            config.create_db = "invalid_create_db"  # type: ignore

    def test_create_table(self):
        """Test the create_table property."""
        config = TableConfig()
        config.create_table = True
        self.assertTrue(config.create_table)
        with self.assertRaises(AssertionError):
            config.create_table = "invalid_create_table"  # type: ignore

    def test_wait_for_db(self):
        """Test the wait_for_db property."""
        config = TableConfig()
        config.wait_for_db = True
        self.assertTrue(config.wait_for_db)
        with self.assertRaises(AssertionError):
            config.wait_for_db = "invalid_wait_for_db"  # type: ignore

    def test_wait_for_table(self):
        """Test the wait_for_table property."""
        config = TableConfig()
        config.wait_for_table = True
        self.assertTrue(config.wait_for_table)
        with self.assertRaises(AssertionError):
            config.wait_for_table = "invalid_wait_for_table"  # type: ignore

    def test_to_json(self):
        """Test the to_json method."""
        config = TableConfig()
        json_config = config.to_json()
        self.assertIsInstance(json_config, dict)
        self.assertIn("database", json_config)
        self.assertIn("table", json_config)
        self.assertIn("schema", json_config)
        self.assertIn("ptr_map", json_config)
        self.assertIn("data_file_folder", json_config)
        self.assertIn("data_files", json_config)
        self.assertIn("delete_db", json_config)
        self.assertIn("delete_table", json_config)
        self.assertIn("create_db", json_config)
        self.assertIn("create_table", json_config)
        self.assertIn("wait_for_db", json_config)
        self.assertIn("wait_for_table", json_config)
        self.assertIn("conversions", json_config)

    def test_database_config_consistency(self):
        """Test the consistency method of DatabaseConfig."""
        config = DatabaseConfig(password=PSWD_FILE)
        config.dbname = "valid_dbname"
        config.host = "localhost"
        config.port = 5432
        config.maintenance_db = "valid_maintenance_db"
        config.retries = 3
        config.user = "valid_user"

    def test_table_config_consistency(self):
        """Test the consistency method of TableConfig."""
        schema = {
            "id": ColumnSchema(db_type="INTEGER", primary_key=True),
            "name": ColumnSchema(db_type="VARCHAR", unique=True),
        }
        ptr_map = {"id": "name"}
        config = TableConfig(
            database=DatabaseConfig(password=PSWD_FILE),
            table="valid_table",
            schema=schema,
            ptr_map=ptr_map,
            delete_db=True,
            create_db=True,
            create_table=True,
        )
        config.consistency()  # Should not raise any exceptions

    def test_table_config_consistency_invalid_ptr_map(self):
        """Test the consistency method with invalid ptr_map."""
        schema = {
            "id": ColumnSchema(db_type="INTEGER", primary_key=True),
            "name": ColumnSchema(db_type="VARCHAR", unique=True),
        }
        ptr_map = {"id": "non_existent_field"}
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                schema=schema,
                ptr_map=ptr_map,
            )

    def test_table_config_consistency_circular_reference(self):
        """Test the consistency method with circular reference in ptr_map."""
        schema = {
            "id": ColumnSchema(db_type="INTEGER", primary_key=True),
            "name": ColumnSchema(db_type="VARCHAR", unique=True),
        }
        ptr_map = {"id": "name", "name": "id"}
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                schema=schema,
                ptr_map=ptr_map,
            )

    def test_table_config_consistency_delete_db_without_create_db(self):
        """Test the consistency method with delete_db without create_db."""
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                delete_db=True,
                create_table=True,
            )

    def test_table_config_consistency_delete_db_with_wait_for_db(self):
        """Test the consistency method with delete_db and wait_for_db."""
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                delete_db=True,
                create_db=True,
                wait_for_db=True,
                create_table=True,
            )

    def test_table_config_consistency_delete_table_without_create_table(self):
        """Test the consistency method with delete_table without create_table."""
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                delete_table=True,
            )

    def test_table_config_consistency_create_db_with_wait_for_db(self):
        """Test the consistency method with create_db and wait_for_db."""
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                create_db=True,
                wait_for_db=True,
            )

    def test_table_config_consistency_create_table_with_wait_for_table(self):
        """Test the consistency method with create_table and wait_for_table."""
        with self.assertRaises(ValueError):
            TableConfig(
                database=DatabaseConfig(password=PSWD_FILE),
                table="valid_table",
                create_table=True,
                wait_for_table=True,
            )
