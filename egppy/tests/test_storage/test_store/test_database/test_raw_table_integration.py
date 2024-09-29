"""Unit tests for raw_table.py."""

from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy
from inspect import stack
from itertools import count
from json import load
from logging import NullHandler, getLogger
from os.path import dirname, join

from psycopg2 import ProgrammingError, errors
from egppy.storage.store.database.raw_table import RawTable, default_config
from egppy.storage.store.database.configuration import TableConfig
from egppy.storage.store.database.database import db_transaction


_logger = getLogger(__name__)
_logger.addHandler(NullHandler())


_CONFIG = TableConfig(
    {
        "database": {"dbname": "test_db"},
        "table": "test_table",
        "schema": {
            "name": {"type": "VARCHAR", "nullable": True},
            "id": {"type": "INTEGER", "primary_key": True},
            "left": {"type": "INTEGER", "nullable": True},
            "right": {"type": "INTEGER", "nullable": True},
            "uid": {
                "type": "INTEGER",
                "index": "btree",
                "unique": True,
            },
            "updated": {"type": "TIMESTAMP", "default": "NOW()"},
            "metadata": {"type": "INTEGER[]", "index": "btree", "nullable": True},
        },
        "ptr_map": {"left": "id", "right": "id"},
        "data_file_folder": join(dirname(__file__), "data"),
        "data_files": ["data_values.json", "data_empty.json"],
        "delete_db": False,
        "delete_table": True,
        "create_db": True,
        "create_table": True,
        "wait_for_db": False,
        "wait_for_table": False,
    }
)


with open(join(dirname(__file__), "data/data_values.json"), "r", encoding="utf-8") as fileptr:
    _DEFAULT_TABLE_LENGTH = len(load(fileptr))


class RawTableIntegrationTest(TestCase):
    """Test the RawTable class."""

        def test_create_table(self) -> None:
            """Validate the SQL sequence when a table exists."""
            _logger.debug(stack()[0][3])
            config = deepcopy(_CONFIG)
            rt = RawTable(config)
            self.assertIsNotNone(rt)

    @patch.object(RawTable, "_table_exists", side_effect=[False, False, True])
    def test_wait_for_table_creation(self, mock_table_exists) -> None:
        """Wait for the table to be created.

        Create the table then set wait_for_table to True.
        Mock self._table_exists() to return False for the __init__() check
        and the first self._table_definition() check to force a single backoff.
        """
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        config["wait_for_table"] = True
        config["create_table"] = False
        config["delete_table"] = False

        rt = RawTable(config)
        self.assertIsNotNone(rt)

    @patch.object(RawTable, "_db_exists", side_effect=[True, True, False, True, True])
    def test_wait_for_db_creation(self, mock_db_exists) -> None:
        """Wait for the database to be created.

        Make sure the DB exists by creating a table.
        Mock self._db_exists() to return True for the __init__() check, self.delete_table()
        check and false in the first self._table_exists() check to force a single backoff.
        """
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rawt = RawTable(config)
        config["wait_for_db"] = True
        config["create_db"] = False
        config["delete_db"] = False

        rawt = RawTable(config)
        self.assertIsNotNone(rawt)

    @patch.object(RawTable, "_db_transaction")
    def test_create_table_error_1(self, mock_db_transaction) -> None:
        """Raise a ProgrammingError when trying to create the table."""
        _logger.debug(stack()[0][3])
        rt = RawTable(_CONFIG)
        config = deepcopy(rt.config)

        def mock_db_transaction_side_effect(self, sql_str, read=True, ctype="tuple"):
            if "CREATE TABLE " in self._sql_to_string(sql_str):  # pylint: disable=protected-access
                raise ProgrammingError
            return db_transaction(
                config["database"]["dbname"], config["database"], sql_str, read, ctype=ctype
            )

        mock_db_transaction.side_effect = mock_db_transaction_side_effect

        with self.assertRaises(ProgrammingError):
            RawTable(config)

    @patch.object(RawTable, "_db_transaction")
    @patch.object(RawTable, "_table_definition", return_value=[])
    def test_create_table_error_2(self, mock_table_definition, mock_db_transaction):
        """Raise a ProgrammingError with a duplicate table code when trying to create the table."""
        _logger.debug(stack()[0][3])
        rt = RawTable(_CONFIG)
        config = deepcopy(rt.config)

        def mock_db_transaction_side_effect(self, sql_str, read=True, ctype="tuple"):
            if "CREATE TABLE " in self._sql_to_string(sql_str):  # pylint: disable=protected-access
                ProgrammingError.pgcode = errors.DuplicateTable  # pylint: disable=no-member, type: ignore
                raise ProgrammingError
            return db_transaction(
                config["database"]["dbname"], config["database"], sql_str, read, ctype=ctype
            )

        mock_db_transaction.side_effect = mock_db_transaction_side_effect

        assert RawTable(config) is not None

    def test_existing_table_unmatched_config():
        """Try and instanciate a table object using a config that does not match the existing table."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        RawTable(config)
        del config["schema"]["updated"]
        config["delete_table"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05001" in str(e)
        else:
            assert False

    def test_existing_table_primary_key_mismatch():
        """Try and instanciate a table object using a config that defines the wrong primary key."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        RawTable(config)
        config["schema"]["id"]["primary_key"] = False
        config["delete_table"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05002" in str(e)
        else:
            assert False

    def test_existing_table_unique_mismatch():
        """Try and instanciate a table object using a config that defines the wrong unique."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        RawTable(config)
        config["schema"]["left"]["unique"] = True
        config["delete_table"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05003" in str(e)
        else:
            assert False

    def test_existing_table_nullable_mismatch():
        """Try and instanciate a table object using a config that defines the wrong nullable."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        RawTable(config)
        config["schema"]["left"]["nullable"] = False
        config["delete_table"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05004" in str(e)
        else:
            assert False

    def test_len():
        """Make sure the table length is returned."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        assert len(rt) == _DEFAULT_TABLE_LENGTH

    def test_select_1():
        """As it says on the tin - with a column tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        data = rt.select("WHERE {id} = {seven}", {"seven": 7}, columns=("uid", "left", "right"))
        assert list(data) == [(107, 13, None)]

    def test_select_2():
        """As it says on the tin - with a column string."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        data = rt.select("WHERE {id} = {seven}", {"seven": 7}, columns="{uid}, {left}, {right}")
        assert list(data) == [(107, 13, None)]

    def test_literals_error():
        """Literals cannot have keys the same as column names."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        try:
            rt.select("WHERE {id} = {left}", {"left": 7}, columns=("uid", "left", "right"))
        except ValueError:
            pass
        else:
            assert False

    def test_recursive_select_1():
        """As it says on the tin - with a columns tuple."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        data = rt.recursive_select("WHERE {id} = 2", columns=("id", "uid", "left", "right"))
        assert list(data) == [
            (2, 102, 5, 6),
            (5, 105, 10, 11),
            (6, 106, None, 12),
            (10, 110, None, None),
            (11, 111, None, None),
            (12, 112, None, None),
        ]

    def test_recursive_select_2():
        """As it says on the tin - with a column default ('*')."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        data = rt.recursive_select("WHERE {id} = 2")
        assert len(tuple(data)) == 6

    def test_recursive_select_no_ptr():
        """As it says on the tin - missing a ptr_map column."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        data = rt.recursive_select("WHERE {id} = 2", columns=("id", "uid", "left"))
        assert list(data) == [
            (2, 102, 5, 6),
            (5, 105, 10, 11),
            (6, 106, None, 12),
            (10, 110, None, None),
            (11, 111, None, None),
            (12, 112, None, None),
        ]

    def test_insert():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (92, 5, 6, 902, [], "William"))
        rt.insert(columns, values)
        data = tuple(rt.select("WHERE {id} > 90", columns=columns))
        assert data == values

    def test_upsert():
        """Can only upsert if a primary key is defined."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["schema"]["id"]["primary_key"] = False
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (0, 1, 2, 201, [], "Diana"))
        try:
            rt.upsert(
                columns,
                values,
                "{name}={EXCLUDED.name} || {temp}",
                {"temp": "_temp"},
                ("uid", "id", "name"),
            )
        except ValueError:
            pass
        else:
            assert False

    def test_upsert_error():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
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
        assert list(returning) == [(901, 91, "Harry"), (100, 0, "Diana_temp")]
        assert list(row) == [(0, 1, 2, 100, None, "Diana_temp")]

    def test_update():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
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
        assert list(returning) == [(0, "root_new")]
        assert list(row) == [(0, 1, 2, 100, None, "root_new")]

    def test_delete():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        returning = rt.delete("{id}={target}", {"target": 7}, ("uid", "id"))
        row = rt.select(
            "WHERE {id} = 7", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        assert list(returning) == [(107, 7)]
        assert not list(row)

    def test_upsert_returning_all():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = ((91, 3, 4, 901, [1, 2], "Harry"), (0, 1, 2, 201, [], "Diana"))
        returning = rt.upsert(
            columns, values, "{name}={EXCLUDED.name} || {temp}", {"temp": "_temp"}, "*"
        )
        row = rt.select(
            "WHERE {id} = 0", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        # deepcode ignore unguarded~next~call: mock
        assert len(next(returning)) == 7
        assert list(row) == [(0, 1, 2, 100, None, "Diana_temp")]

    def test_update_returning_all():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        returning = rt.update(
            "{name}={name} || {new}", "{id}={qid}", {"qid": 0, "new": "_new"}, "*"
        )
        row = rt.select(
            "WHERE {id} = 0", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        # deepcode ignore unguarded~next~call: mock
        assert len(next(returning)) == 7
        assert list(row) == [(0, 1, 2, 100, None, "root_new")]

    def test_delete_returning_all():
        """As it says on the tin."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        returning = rt.delete("{id}={target}", {"target": 7}, "*")
        row = rt.select(
            "WHERE {id} = 7", columns=("id", "left", "right", "uid", "metadata", "name")
        )
        # deepcode ignore unguarded~next~call: mock
        assert len(next(returning)) == 7
        assert not list(row)

    def test_duplicate_table():
        """Validate a the SQL sequence when a table exists."""
        _logger.debug(stack()[0][3])
        config1 = deepcopy(_CONFIG)
        config2 = deepcopy(_CONFIG)
        config2["delete_table"] = False
        rt1 = RawTable(config1)
        rt2 = RawTable(config2)
        for t1, t2 in zip(
            # deepcode ignore unguarded~next~call: mock
            next(rt1.select(columns=("updated",))),
            # deepcode ignore unguarded~next~call: mock
            next(rt2.select(columns=("updated",))),
        ):
            assert t1 == t2
        rt1.delete_table()
        rt2.delete_table()

    def test_discover_table():
        """Validate table discovery.

        Create a table rt1 and fill it with some data.
        Instanciate a table rt2 with no schema from the same DB & table name as rt1.
        rt1 and rt2 should point at the same table.
        """
        _logger.debug(stack()[0][3])
        config1 = deepcopy(_CONFIG)
        config1["data_files"] = []
        rt1 = RawTable(config1)
        columns = ("id", "left", "right", "uid", "metadata", "name")
        values = [(91, 3, 4, 901, [1, 2], "Harry"), (92, 5, 6, 902, [], "William")]
        rt1.insert(columns, values)
        rt2 = RawTable(TableConfig({"database": _CONFIG["database"], "table": _CONFIG["table"]}))
        data = rt2.select(columns=columns)
        assert list(data) == values
        values.append((0, 1, 2, 201, [], "Diana"))
        rt2.insert(columns, [values[-1]])
        data = rt1.select(columns=columns)
        assert list(data) == values

    def test_config_coercion():
        """If PRIMARY KEY is set UNIQUE is coerced to True."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        rt = RawTable(config)
        assert rt.config["schema"]["id"]["unique"]

    def test_invalid_config_1():
        """Invalid database configuration."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["database"]["port"] = 100
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_2():
        """General invalid schema column configuration."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        del config["schema"]["name"]["type"]
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_3():
        """Invalid schema column configuration: NULL & PRIMARY KEY."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["schema"]["id"]["nullable"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_4():
        """Invalid schema column configuration: Multiple primary keys."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["schema"]["name"]["primary_key"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_5():
        """Invalid schema column configuration: Ptr map circular reference."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["ptr_map"]["id"] = "left"
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_6():
        """Invalid schema column configuration: Ptr map value is not a column."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["ptr_map"]["left"] = "invalid"
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_7():
        """Invalid schema column configuration: Ptr map key is not a column."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["ptr_map"]["invalid"] = "id"
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_8():
        """Invalid schema column configuration: DB delete requires DB create."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["delete_db"] = True
        config["create_db"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_9():
        """Invalid schema column configuration: Table delete requires table create."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["delete_table"] = True
        config["create_table"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_10():
        """Invalid schema column configuration: DB delete requires table create or wait_for_table."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["delete_db"] = True
        config["create_table"] = False
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_11():
        """Invalid schema column configuration: Create DB requires wait_for_db == False."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["create_db"] = True
        config["wait_for_db"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_12():
        """Invalid schema column configuration: Create table requires wait_for_table == False."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["create_table"] = True
        config["wait_for_table"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_13():
        """Invalid schema column configuration: Wait for DB requires create_db &
        delete_db to be False."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["delete_db"] = True
        config["wait_for_db"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_14():
        """Invalid schema column configuration: Wait for DB requires create_table or
        wait_for_table to be True."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["create_table"] = False
        config["wait_for_table"] = False
        config["wait_for_db"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_15():
        """Invalid schema column configuration: Wait for table requires create_table
        and delete_table to be False."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["create_table"] = True
        config["wait_for_table"] = True
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_invalid_config_16():
        """Invalid schema column configuration: Wait for table requires create_table
        and delete_table to be False."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["data_files"] = ["invalid"]
        try:
            RawTable(config)
        except ValueError as e:
            assert "E05000" in str(e)
            return
        assert False

    def test_delete_create_db():
        """Delete the DB & re-create it."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        config["delete_db"] = True
        config["create_db"] = True
        RawTable(config)

    def test_arbitrary_sql_return():
        """Execute some arbitrary SQL."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        t = RawTable(config)
        result = next(t.arbitrary_sql("SELECT 2.0::REAL * 3.0::REAL"))[0]
        assert result == approx(6.0)

    def test_arbitrary_sql_literals():
        """Execute some arbitrary SQL."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        t = RawTable(config)
        result = next(
            t.arbitrary_sql("SELECT {two}::REAL * {three}::REAL", {"two": 2.0, "three": 3.0})
        )[0]
        assert result == approx(6.0)

    def test_arbitrary_sql_no_return():
        """Execute some arbitrary SQL that returns no result."""
        _logger.debug(stack()[0][3])
        config = deepcopy(_CONFIG)
        t = RawTable(config)
        result = t.arbitrary_sql(
            'INSERT INTO "test_table" ("id","metadata","right","uid")'
            + " VALUES (6,ARRAY[1],12,106) ON CONFLICT DO NOTHING",
            read=False,
        )
        try:
            next(result)
        except ProgrammingError:
            pass
        else:
            assert False

    def test_default_config():
        """Make sure a dictionary is returned."""
        assert isinstance(default_config(), dict)
