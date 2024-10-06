"""Unit tests for raw_table.py."""

from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy
from inspect import stack
from json import load
from logging import NullHandler, getLogger
from os.path import dirname, join
from itertools import count
from psycopg2 import ProgrammingError
from egppy.storage.store.database import database
from egppy.storage.store.database.raw_table import RawTable, default_config
from egppy.storage.store.database.configuration import TableConfig
from egppy.storage.store.database.database import db_transaction


_logger = getLogger(__name__)
_logger.addHandler(NullHandler())


_CONFIG = TableConfig(
    **{
        "database": {"dbname": "test_db"},
        "table": "test_table",
        "schema": {
            "name": {"db_type": "VARCHAR", "nullable": True},
            "id": {"db_type": "INTEGER", "primary_key": True},
            "left": {"db_type": "INTEGER", "nullable": True},
            "right": {"db_type": "INTEGER", "nullable": True},
            "uid": {
                "db_type": "INTEGER",
                "unique": True,
            },
            "updated": {"db_type": "TIMESTAMP", "default": "NOW()"},
            "metadata": {"db_type": "INTEGER[]", "index": "btree", "nullable": True},
        },
        "ptr_map": {"left": "id", "right": "id"},
        "data_file_folder": join(dirname(__file__), "data", ""),
        "data_files": ["data_values.json", "data_empty.json"],
        "delete_db": True,
        "delete_table": True,
        "create_db": True,
        "create_table": True,
        "wait_for_db": False,
        "wait_for_table": False,
    }
)


# To uniquely name databases for parallel execution
_DB_COUNTER = count(1)


with open(join(dirname(__file__), "data/data_values.json"), "r", encoding="utf-8") as fileptr:
    _DEFAULT_TABLE_LENGTH = len(load(fileptr))


class RawTableIntegrationTest(TestCase):
    """Test the RawTable class."""

    def test_create_table(self) -> None:
        """Validate the SQL sequence when a table exists."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        self.assertIsNotNone(rt)

    @patch.object(RawTable, "_table_exists_", side_effect=[False, False, True])
    @patch.object(RawTable, "_table_definition", side_effect=[{"column"}])
    def test_wait_for_table_creation(self, _, __) -> None:
        """Wait for the table to be created.

        Create the table then set wait_for_table to True.
        Mock self._table_exists() to return False for the __init__() check
        and the first self._table_definition() check to force a single backoff.
        """
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        config["wait_for_table"] = True
        config["create_table"] = False
        config["delete_table"] = False

        rt = RawTable(config)
        self.assertIsNotNone(rt)

    def test_create_table_error_1(self) -> None:
        """Raise a ProgrammingError when trying to create the table."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"

        class MockRawTable(RawTable):
            """Mock RawTable class to raise a ProgrammingError when trying to create the table."""

            def _db_transaction(self, sql_str, read=True, ctype="tuple"):
                if "CREATE TABLE " in self._sql_to_string(
                    sql_str
                ):  # pylint: disable=protected-access
                    raise ProgrammingError
                return db_transaction(
                    config["database"]["dbname"], config["database"], sql_str, read, ctype=ctype
                )

        with self.assertRaises(ProgrammingError):
            MockRawTable(config)

    def test_existing_table_unmatched_config(self) -> None:
        """Try and instantiate a table object using a config that does not
        match the existing table."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        RawTable(config)
        del config["schema"]["updated"]
        config["delete_table"] = False
        config["create_table"] = False
        config["delete_db"] = False
        config["create_db"] = False
        with self.assertRaises(ValueError) as context:
            RawTable(config)
        self.assertIn("E05001", str(context.exception))

    def test_existing_table_primary_key_mismatch(self) -> None:
        """Try and instantiate a table object using a config that defines the wrong primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        RawTable(config)
        config["schema"]["id"]["primary_key"] = False
        config["delete_table"] = False
        config["create_table"] = False
        config["delete_db"] = False
        config["create_db"] = False
        with self.assertRaises(ValueError) as context:
            RawTable(config)
        self.assertIn("E05002", str(context.exception))

    def test_existing_table_unique_mismatch(self) -> None:
        """Try and instantiate a table object using a config that defines the wrong unique."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        RawTable(config)
        config["schema"]["left"]["unique"] = True
        config["delete_table"] = False
        config["create_table"] = False
        config["delete_db"] = False
        config["create_db"] = False
        with self.assertRaises(ValueError) as context:
            RawTable(config)
        self.assertIn("E05003", str(context.exception))

    def test_existing_table_nullable_mismatch(self) -> None:
        """Try and instantiate a table object using a config that defines the wrong nullable."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        RawTable(config)
        config["schema"]["left"]["nullable"] = False
        config["delete_table"] = False
        config["create_table"] = False
        config["delete_db"] = False
        config["create_db"] = False
        with self.assertRaises(ValueError) as context:
            RawTable(config)
        self.assertIn("E05004", str(context.exception))

    def test_len(self) -> None:
        """Make sure the table length is returned."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        self.assertEqual(len(rt), _DEFAULT_TABLE_LENGTH)

    def test_select_1(self) -> None:
        """As it says on the tin - with a column tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        data = rt.select("WHERE {id} = {seven}", {"seven": 7}, columns=("uid", "left", "right"))
        self.assertEqual(list(data), [(107, 13, None)])

    def test_select_2(self) -> None:
        """As it says on the tin - with a column string."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        data = rt.select("WHERE {id} = {seven}", {"seven": 7}, columns="{uid}, {left}, {right}")
        self.assertEqual(list(data), [(107, 13, None)])

    def test_literals_error(self) -> None:
        """Literals cannot have keys the same as column names."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        with self.assertRaises(ValueError):
            rt.select("WHERE {id} = {left}", {"left": 7}, columns=("uid", "left", "right"))

    def test_recursive_select_1(self) -> None:
        """As it says on the tin - with a columns tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        data = rt.recursive_select("WHERE {id} = 2", columns=("id", "uid", "left", "right"))
        self.assertEqual(
            list(data),
            [
                (2, 102, 5, 6),
                (5, 105, 10, 11),
                (6, 106, None, 12),
                (10, 110, None, None),
                (11, 111, None, None),
                (12, 112, None, None),
            ],
        )

    def test_recursive_select_2(self) -> None:
        """As it says on the tin - with a column default ('*')."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        data = rt.recursive_select("WHERE {id} = 2")
        self.assertEqual(len(tuple(data)), 6)

    def test_recursive_select_no_ptr(self) -> None:
        """As it says on the tin - missing a ptr_map column."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        data = rt.recursive_select("WHERE {id} = 2", columns=("id", "uid", "left"))
        self.assertEqual(
            list(data),
            [
                (2, 102, 5, 6),
                (5, 105, 10, 11),
                (6, 106, None, 12),
                (10, 110, None, None),
                (11, 111, None, None),
                (12, 112, None, None),
            ],
        )

    def test_insert(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (92, 5, 6, 902, [], "William"))
        rt.insert(columns, values)
        data = tuple(rt.select("WHERE {id} > 90", columns=columns))
        self.assertEqual(data, values)

    def test_upsert(self) -> None:
        """Can only upsert if a primary key is defined."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        config["schema"]["id"]["primary_key"] = False
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (0, 1, 2, 201, [], "Diana"))
        with self.assertRaises(ValueError):
            rt.upsert(
                columns,
                values,
                "{name}={EXCLUDED.name} || {temp}",
                {"temp": "_temp"},
                ("uid", "id", "name"),
            )

    def test_upsert_error(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (0, 1, 2, 201, [], "Diana"))
        returning = rt.upsert(
            columns,
            values,
            "{name}={EXCLUDED.name} || {temp}",
            {"temp": "_temp"},
            ("uid", "id", "name"),
        )
        row = rt.select(
            "WHERE {id} = 0", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        self.assertEqual(list(returning), [(901, 91, "Harry"), (100, 0, "Diana_temp")])
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "Diana_temp")])

    def test_update(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        returning = rt.update(
            "{name}={name} || {new}",
            "{id}={qid}",
            {"qid": 0, "new": "_new"},
            ("id", "name"),
        )
        row = rt.select(
            "WHERE {id} = 0", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        self.assertEqual(list(returning), [(0, "root_new")])
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "root_new")])

    def test_delete(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        returning = rt.delete("{id}={target}", {"target": 7}, ("uid", "id"))
        row = rt.select(
            "WHERE {id} = 7", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        self.assertEqual(list(returning), [(107, 7)])
        self.assertFalse(list(row))

    def test_upsert_returning_all(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (0, 1, 2, 201, [], "Diana"))
        returning = rt.upsert(
            columns, values, "{name}={EXCLUDED.name} || {temp}", {"temp": "_temp"}, "*"
        )
        row = rt.select(
            "WHERE {id} = 0", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        self.assertEqual(len(next(returning)), 7)
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "Diana_temp")])

    def test_update_returning_all(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        returning = rt.update(
            "{name}={name} || {new}", "{id}={qid}", {"qid": 0, "new": "_new"}, "*"
        )
        row = rt.select(
            "WHERE {id} = 0", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        self.assertEqual(len(next(returning)), 7)
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "root_new")])

    def test_delete_returning_all(self) -> None:
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        returning = rt.delete("{id}={target}", {"target": 7}, "*")
        row = rt.select(
            "WHERE {id} = 7", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        self.assertEqual(len(next(returning)), 7)
        self.assertFalse(list(row))

    def test_duplicate_table(self) -> None:
        """Validate the SQL sequence when a table exists."""
        _logger.debug(stack()[0][3])
        config1 = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config1["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        config2 = deepcopy(config1)
        config2["delete_table"] = False
        rt1 = RawTable(config1)
        rt2 = RawTable(config2)
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        t1 = next(rt1.select(columns=("updated",)))
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        t2 = next(rt2.select(columns=("updated",)))
        self.assertEqual(t1, t2)
        rt1.delete_table()
        rt2.delete_table()

    def test_discover_table(self) -> None:
        """Validate table discovery.

        Create a table rt1 and fill it with some data.
        Instantiate a table rt2 with no schema from the same DB & table name as rt1.
        rt1 and rt2 should point at the same table.
        """
        _logger.debug(stack()[0][3])
        config1 = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config1["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        config1["data_files"] = []
        rt1 = RawTable(config1)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = [(91, 3, 4, 901, [1, 2], "Harry"), (92, 5, 6, 902, [], "William")]
        rt1.insert(columns, values)
        rt2 = RawTable(TableConfig(**{"database": config1["database"], "table": config1["table"]}))
        data = rt2.select(columns=columns)
        self.assertEqual(list(data), values)
        values.append((0, 1, 2, 201, [], "Diana"))
        rt2.insert(columns, [values[-1]])
        data = rt1.select(columns=columns)
        self.assertEqual(list(data), values)

    def test_config_coercion(self) -> None:
        """If PRIMARY KEY is set UNIQUE is coerced to True."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = RawTable(config)
        self.assertTrue(rt.config["schema"]["id"]["unique"])

    def test_delete_create_db(self) -> None:
        """Delete the DB & re-create it."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        config["delete_db"] = True
        config["create_db"] = True
        RawTable(config)

    def test_arbitrary_sql_return(self) -> None:
        """Execute some arbitrary SQL."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = RawTable(config)
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        result = next(t.arbitrary_sql("SELECT 2.0::REAL * 3.0::REAL"))[0]
        self.assertAlmostEqual(result, 6.0)

    def test_arbitrary_sql_literals(self) -> None:
        """Execute some arbitrary SQL."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = RawTable(config)
        # deepcode ignore unguarded~next~call: test case will fail if next() raises StopIteration
        result = next(
            t.arbitrary_sql("SELECT {two}::REAL * {three}::REAL", {"two": 2.0, "three": 3.0})
        )[0]
        self.assertAlmostEqual(result, 6.0)

    def test_arbitrary_sql_no_return(self) -> None:
        """Execute some arbitrary SQL that returns no result."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = RawTable(config)
        result = t.arbitrary_sql(
            'INSERT INTO "test_table" ("id","metadata","right","uid")'
            + " VALUES (6,ARRAY[1],12,106) ON CONFLICT DO NOTHING",
            read=False,
        )
        with self.assertRaises(ProgrammingError):
            # deepcode ignore unguarded~next~call: test case will fail if next() raises
            next(result)

    def test_default_config(self) -> None:
        """Make sure a dictionary is returned."""
        assert isinstance(default_config(), TableConfig)
