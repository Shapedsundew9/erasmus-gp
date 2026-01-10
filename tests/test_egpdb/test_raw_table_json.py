"""Integration tests for JSON/JSONB support in raw_table.py."""

from copy import deepcopy
from inspect import stack
from itertools import count, islice
from logging import NullHandler, getLogger
from unittest import TestCase

from psycopg2.extras import Json

from egpdb.configuration import TableConfig
from egpdb.database import db_delete
from egpdb.raw_table import RawTable

_logger = getLogger(__name__)
_logger.addHandler(NullHandler())

_CONFIG = TableConfig(
    **{
        "database": {"dbname": "test_db_json", "host": "postgres"},
        "table": "test_table_json",
        "schema": {
            "id": {"db_type": "SERIAL", "primary_key": True},
            "data_json": {"db_type": "JSON", "nullable": True},
            "data_jsonb": {"db_type": "JSONB", "nullable": True},
        },
        "ptr_map": {},
        "data_file_folder": "",
        "data_files": [],
        "delete_db": True,
        "delete_table": True,
        "create_db": True,
        "create_table": True,
        "wait_for_db": False,
        "wait_for_table": False,
    }
)

_START_DB_COUNTER = 1000
_NUM_DBS = 100
_DB_COUNTER = islice(count(_START_DB_COUNTER), _NUM_DBS)


class RawTableJsonTest(TestCase):
    """Test JSON/JSONB support in RawTable."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the test databases."""
        _logger.debug(stack()[0][3])
        for num in range(next(_DB_COUNTER) - 1, _START_DB_COUNTER - 1, -1):
            db_delete(f"test_db_json_{num}", _CONFIG["database"])

    def _get_config(self):
        config = deepcopy(_CONFIG)
        config["database"]["dbname"] = f"test_db_json_{next(_DB_COUNTER)}"
        return config

    def test_insert_select_json(self) -> None:
        """Test inserting and selecting JSON data (dicts and lists)."""
        config = self._get_config()
        rt = RawTable(config)

        columns = ("data_json", "data_jsonb")
        values = [
            ({"key": "value", "list": [1, 2, 3]}, ["a", "b", "c"]),
            ([1, 2, 3], {"nested": {"a": 1}}),
            (None, None),
        ]

        rt.insert(columns, values)

        # Order by id to ensure deterministic order
        results = list(rt.select(columns=columns, query_str="ORDER BY id"))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], values[0])
        self.assertEqual(results[1], values[1])
        self.assertEqual(results[2], (None, None))

    def test_update_json(self) -> None:
        """Test updating JSON data."""
        config = self._get_config()
        rt = RawTable(config)

        # Insert a JSON array (list of dicts)
        # Note: values must be iterable of rows. Each row is iterable of values.
        # To insert a list into a column, the row must contain that list.
        rt.insert(("data_jsonb",), [([{"a": 1}],)])

        # Verify insert
        initial = list(rt.select(columns=("data_jsonb",)))
        # print(f"Initial data: {initial}")

        # Update using a dict (auto adapted)
        rt.update("{data_jsonb} = {new_val}", "{data_jsonb}->0->>'a' = '1'", {"new_val": {"b": 2}})

        res = list(rt.select(columns=("data_jsonb",)))
        # print(f"After update 1: {res}")
        self.assertEqual(res[0][0], {"b": 2})

        # Update using a list (requires wrapper or cast)
        # Using Json wrapper
        rt.update("{data_jsonb} = {new_val}", None, {"new_val": Json([1, 2, 3])})

        res = list(rt.select(columns=("data_jsonb",)))
        self.assertEqual(res[0][0], [1, 2, 3])

    def test_json_operators(self) -> None:
        """Test JSON operators in WHERE clause."""
        config = self._get_config()
        rt = RawTable(config)

        values = [({"type": "A", "val": 1},), ({"type": "B", "val": 2},)]
        rt.insert(("data_jsonb",), values)

        # Select where type is A. Note: ->> returns text.
        res = list(rt.select("WHERE {data_jsonb}->>'type' = 'A'", columns=("data_jsonb",)))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], values[0][0])
