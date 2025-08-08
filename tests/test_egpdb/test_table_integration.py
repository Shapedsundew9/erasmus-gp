"""Unit tests for raw_table.py."""

from copy import deepcopy
from inspect import stack
from itertools import count, islice
from json import load
from logging import NullHandler, getLogger
from os.path import dirname, join
from unittest import TestCase

from egpdb.configuration import TableConfig
from egpdb.database import db_delete
from egpdb.table import Table

_logger = getLogger(__name__)
_logger.addHandler(NullHandler())


_CONFIG = TableConfig(
    **{
        "database": {"dbname": "test_db", "host": "postgres"},
        "table": "test_table",
        "schema": {
            "name": {"db_type": "VARCHAR", "nullable": True},
            "id": {"db_type": "INTEGER", "primary_key": True},
            "left": {"db_type": "INTEGER", "nullable": True},
            "right": {"db_type": "INTEGER", "nullable": True},
            "uid": {"db_type": "INTEGER", "index": "btree"},
            "updated": {"db_type": "TIMESTAMP", "default": "NOW()"},
            "metadata": {"db_type": "INTEGER[]", "index": "btree", "nullable": True},
        },
        "ptr_map": {"left": "id", "right": "id"},
        "data_file_folder": join(dirname(__file__), "data"),
        "data_files": ["data_values.json"],
        "delete_db": True,
        "delete_table": True,
        "create_db": True,
        "create_table": True,
        "wait_for_db": False,
        "wait_for_table": False,
    }
)


# To uniquely name databases for parallel execution
_START_DB_COUNTER = 1000
_NUM_DBS = 100
_DB_COUNTER = islice(count(_START_DB_COUNTER), _NUM_DBS)


with open(join(dirname(__file__), "data/data_values.json"), "r", encoding="utf-8") as fileptr:
    _DEFAULT_TABLE_LENGTH = len(load(fileptr))


def _register_conversions(table):
    table.register_conversion("id", lambda x: x - 1000, lambda x: x + 1000)
    table.register_conversion("name", lambda x: x.lower(), lambda x: x.upper())
    return table


class TableIntegrationTest(TestCase):
    """Integration tests for the Table class."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the test databases."""
        _logger.debug(stack()[0][3])
        # deepcode ignore unguarded~next~call: infinite counter
        for num in range(next(_DB_COUNTER) - 1, _START_DB_COUNTER - 1, -1):
            db_delete(f"test_db_{num}", _CONFIG["database"])

    def test_create_table(self) -> None:
        """Validate the SQL sequence when a table exists."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        self.assertIsNotNone(t)

    def test_len(self) -> None:
        """Make sure the table length is returned."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        rt = Table(config)
        self.assertEqual(len(rt), _DEFAULT_TABLE_LENGTH)

    def test_getitem_encoded_pk1(self) -> None:
        """Validate a valid getitem for an encoded primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = _register_conversions(Table(config))
        expected = {
            "id": 1000,
            "left": 1,
            "right": 2,
            "uid": 100,
            "metadata": None,
            "name": "ROOT",
        }
        result = t[1000]
        self.assertTrue(all(result[k] == v for k, v in expected.items()))

    def test_getitem_encoded_pk2(self) -> None:
        """Validate an invalid getitem for an encoded primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = _register_conversions(Table(config))
        with self.assertRaises(KeyError):
            _ = t[0]

    def test_getitem_pk1(self) -> None:
        """Validate a valid getitem."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        expected = {
            "id": 0,
            "left": 1,
            "right": 2,
            "uid": 100,
            "metadata": None,
            "name": "root",
        }
        result = t[0]
        self.assertTrue(all(result[k] == v for k, v in expected.items()))

    def test_getitem_pk2(self) -> None:
        """Validate an invalid getitem."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        with self.assertRaises(KeyError):
            _ = t[1000]

    def test_getitem_no_pk(self) -> None:
        """Validate if the table has no primary key we get the correct ValueError."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["schema"]["id"]["primary_key"] = False
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        with self.assertRaises(ValueError) as context:
            _ = t[0]
        self.assertEqual(
            str(context.exception), "SELECT row on primary key but no primary key defined!"
        )

    def test_setitem_encoded_pk(self) -> None:
        """Validate a valid setitem for an encoded primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = _register_conversions(Table(config))
        setitem = {
            "id": 22,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        expected_decoded = {
            "id": 22,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "ROOT",
        }
        expected_raw = {
            "id": -978,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "root",
        }
        t[22] = setitem
        result = t[22]
        # deepcode ignore unguarded~next~call: test case
        raw_result = dict(zip(t.raw.columns, next(t.raw.select("WHERE {id} = -978")), strict=True))
        self.assertTrue(all(result[k] == v for k, v in expected_decoded.items()))
        self.assertTrue(all(raw_result[k] == v for k, v in expected_raw.items()))

    def test_setitem_pk(self) -> None:
        """Validate a valid setitem."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        setitem = {
            "id": 22,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        expected_decoded = {
            "id": 22,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        expected_raw = {
            "id": 22,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        t[22] = setitem
        result = t[22]
        # deepcode ignore unguarded~next~call: test case
        raw_result = dict(zip(t.raw.columns, next(t.raw.select("WHERE {id} = 22")), strict=True))
        self.assertTrue(all(result[k] == v for k, v in expected_decoded.items()))
        self.assertTrue(all(raw_result[k] == v for k, v in expected_raw.items()))

    def test_setitem_mismatch_pk(self) -> None:
        """When setting an item and specifying the primary key in the
        value the setitem key takes precedence."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        setitem = {
            "id": 22,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        expected_decoded = {
            "id": 28,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        expected_raw = {
            "id": 28,
            "left": 9,
            "right": 12,
            "uid": 122,
            "metadata": [34, 78],
            "name": "rOoT",
        }
        t[28] = setitem
        result = t[28]
        # deepcode ignore unguarded~next~call: test case
        raw_result = dict(zip(t.raw.columns, next(t.raw.select("WHERE {id} = 28")), strict=True))
        self.assertTrue(all(result[k] == v for k, v in expected_decoded.items()))
        self.assertTrue(all(raw_result[k] == v for k, v in expected_raw.items()))
        with self.assertRaises(KeyError):
            _ = t[22]

    def test_select_tuple(self) -> None:
        """Validate select returning a tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = list(
            t.select(
                "WHERE {id} = {seven}",
                {"seven": 7},
                columns=("uid", "left", "right"),
                container="tuple",
            )
        )
        self.assertEqual(data, [(107, 13, None)])

    def test_select_dict(self) -> None:
        """Validate select returning a dict."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = list(
            t.select(
                "WHERE {id} = {seven}",
                {"seven": 7},
                columns=("uid", "left", "right"),
                container="dict",
            )
        )
        self.assertEqual(data, [{"uid": 107, "left": 13, "right": None}])

    def test_select_all_columns(self):
        """Validate select returning all columns using '*' (the default)."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = tuple(t.select(container="tuple"))
        self.assertEqual(len(data[0]), len(t.columns()))

    def test_recursive_select(self):
        """Validate a recursive select returning a tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = list(
            t.recursive_select(
                "WHERE {id} = 2", columns=("id", "uid", "left", "right"), container="tuple"
            )
        )
        self.assertEqual(
            data,
            [
                (2, 102, 5, 6),
                (5, 105, 10, 11),
                (6, 106, None, 12),
                (10, 110, None, None),
                (11, 111, None, None),
                (12, 112, None, None),
            ],
        )

    def test_recursive_select_no_pk(self) -> None:
        """Validate a recursive select returning a pkdict without specifying the primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = tuple(
            t.recursive_select(
                "WHERE {id} = 2", columns=("uid", "left", "right"), container="pkdict"
            )
        )
        self.assertTrue(len(data))

    def test_upsert(self) -> None:
        """Validate an upsert consisting of 1 insert & 1 update
        returning updated fields as tuples."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = (
            {
                "id": 91,
                "left": 3,
                "right": 4,
                "uid": 901,
                "metadata": [1, 2],
                "name": "Harry",
            },
            {"id": 0, "left": 1, "right": 2, "uid": 201, "metadata": [], "name": "Diana"},
        )
        returning = t.upsert(
            data,
            "{name}={EXCLUDED.name} || {temp}",
            {"temp": "_temp"},
            ("uid", "id", "name"),
            container="tuple",
        )
        row = t.select(
            "WHERE {id} = 0",
            columns=("id", "left", "right", "uid", "metadata", "name"),
            container="tuple",
        )
        self.assertEqual(list(returning), [(901, 91, "Harry"), (100, 0, "Diana_temp")])
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "Diana_temp")])

    def test_upsert_no_pk(self) -> None:
        """Validate an upsert returning a pkdict without specifying the primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        data = (
            {
                "id": 91,
                "left": 3,
                "right": 4,
                "uid": 901,
                "metadata": [1, 2],
                "name": "Harry",
            },
            {"id": 0, "left": 1, "right": 2, "uid": 201, "metadata": [], "name": "Diana"},
        )
        returning = tuple(
            t.upsert(
                data,
                "{name}={EXCLUDED.name} || {temp}",
                {"temp": "_temp"},
                ("uid", "name"),
                container="invalid_so_dict",
            )
        )
        row = list(
            t.select(
                "WHERE {id} = 0",
                columns=("id", "left", "right", "uid", "metadata", "name"),
                container="tuple",
            )
        )
        self.assertEqual(len(returning), 2)
        self.assertIsInstance(returning[0], dict)
        self.assertEqual(row, [(0, 1, 2, 100, None, "Diana_temp")])

    def test_insert(self) -> None:
        """Validate inserting two rows from a dict."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        data = [
            {
                "id": 91,
                "left": 3,
                "right": 4,
                "uid": 901,
                "metadata": [1, 2],
                "name": "Harry",
            },
            {
                "id": 92,
                "left": 5,
                "right": 6,
                "uid": 902,
                "metadata": [],
                "name": "William",
            },
        ]
        t.insert(data)
        results = list(t.select("WHERE {id} > 90 ORDER BY {id} ASC", columns=columns))
        self.assertEqual(data, results)

    def test_update(self) -> None:
        """Validate an update returning a dict."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        returning = t.update(
            "{name}={name} || {new}",
            "{id}={qid}",
            {"qid": 0, "new": "_new"},
            ("id", "name"),
            container="dict",
        )
        row = t.select(
            "WHERE {id} = 0",
            columns=("id", "left", "right", "uid", "metadata", "name"),
            container="tuple",
        )
        self.assertEqual(list(returning), [{"id": 0, "name": "root_new"}])
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "root_new")])

    def test_update_all_rows(self) -> None:
        """Validate an update returning a dict."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        returning = t.update(
            "{left}={left}*{left}", literals={}, returning=("id", "left"), container="dict"
        )
        row = t.select(
            "WHERE {id} = 0",
            columns=("id", "left", "right", "uid", "metadata", "name"),
            container="tuple",
        )
        self.assertEqual(
            list(returning),
            [
                {"id": 0, "left": 1},
                {"id": 1, "left": 9},
                {"id": 2, "left": 25},
                {"id": 4, "left": 64},
                {"id": 5, "left": 100},
                {"id": 3, "left": 49},
                {"id": 7, "left": 169},
                {"id": 6, "left": None},
                {"id": 8, "left": None},
                {"id": 9, "left": None},
                {"id": 10, "left": None},
                {"id": 11, "left": None},
                {"id": 12, "left": None},
                {"id": 13, "left": None},
            ],
        )
        self.assertEqual(list(row), [(0, 1, 2, 100, None, "root")])

    def test_delete(self) -> None:
        """Validate a delete returning a tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        returning = t.delete("{id}={target}", {"target": 7}, ("uid", "id"), container="tuple")
        row = t.select("WHERE {id} = 7", columns=("id", "left", "right", "uid", "metadata", "name"))
        self.assertEqual(list(returning), [(107, 7)])
        self.assertEqual(list(row), [])

    def test_delete_no_pk(self) -> None:
        """Validate a delete returning a dict without."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        returning = list(t.delete("{id}={target}", {"target": 7}, ("uid",), container="pkdict"))
        row = t.select("WHERE {id} = 7", columns=("id", "left", "right", "uid", "metadata", "name"))
        self.assertEqual(len(returning), 1)
        self.assertEqual(list(row), [])

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
        t1 = Table(config1)
        values_dict = [
            {
                "id": 91,
                "left": 3,
                "right": 4,
                "uid": 901,
                "metadata": [1, 2],
                "name": "Harry",
            },
            {
                "id": 92,
                "left": 5,
                "right": 6,
                "uid": 902,
                "metadata": [],
                "name": "William",
            },
        ]
        t1.insert(values_dict)
        t2 = Table(TableConfig(**{"database": config1["database"], "table": config1["table"]}))
        data = t2.select(columns=values_dict[0].keys())
        self.assertEqual(list(data), values_dict)
        values_dict.append(
            {"id": 0, "left": 1, "right": 2, "uid": 201, "metadata": [], "name": "Diana"}
        )
        t2.insert([values_dict[-1]])
        data = t1.select(columns=values_dict[0].keys())
        self.assertEqual(list(data), values_dict)

    def test_arbitrary_sql(self) -> None:
        """Execute some arbitrary SQL."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        # deepcode ignore unguarded~next~call: infinite counter
        config["database"]["dbname"] = f"test_db_{next(_DB_COUNTER)}"
        t = Table(config)
        # deepcode ignore unguarded~next~call: test case
        result = next(t.raw.arbitrary_sql("SELECT 2.0::REAL * 3.0::REAL"))[0]
        self.assertAlmostEqual(result, 6.0)
