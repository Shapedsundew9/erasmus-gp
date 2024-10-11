"""Test case for JSONFileStore class."""

import unittest
from collections.abc import Hashable
from copy import deepcopy
from itertools import count

from egppy.storage.store.database.configuration import TableConfig
from egppy.storage.store.database.database import db_create, db_delete
from egppy.storage.store.db_table_store import DBTableStore
from egppy.storage.store.storable_obj import StorableDict
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.store_abc import StoreABC
from tests.test_storage.test_store.json_file_store_test_base import JSONFileStoreTestBase

# To uniquely name databases for parallel execution
# To avoid conflicts with other test modules we just use the range 0 to 999
_START_DB_COUNTER = 2000


_CONFIG = TableConfig(
    **{
        "database": {"dbname": f"test_db_{_START_DB_COUNTER}"},
        "table": "test_table",
        "schema": {
            "pk": {"db_type": "VARCHAR", "primary_key": True},
            "a": {"db_type": "INTEGER"},
            "b": {"db_type": "INTEGER"},
            "c": {"db_type": "INTEGER"},
        },
        "delete_db": False,
        "delete_table": False,
        "create_db": True,
        "create_table": True,
        "wait_for_db": False,
        "wait_for_table": False,
    }
)


class TestDBTableStore(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with StorableDict."""

    store_type = DBTableStore
    value_type = StorableDict
    value: StorableObjABC = StorableDict({"a": 1, "b": 2, "c": 3})
    value1: StorableObjABC = StorableDict({"a": 4, "b": 5, "c": 6})
    value2: StorableObjABC = StorableDict({"a": 7, "b": 8, "c": 9})
    table_counter = count()

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test."""
        db_delete(f"test_db_{_START_DB_COUNTER}", _CONFIG["database"])
        db_create(f"test_db_{_START_DB_COUNTER}", _CONFIG["database"])

    def setUp(self) -> None:
        """Set up the test.

        TODO: Use a table name counter to avoid conflicts.
        Add a teardown method to delete the tables.
        """
        self.store_type: type[StoreABC] = DBTableStore
        config = _CONFIG.copy()
        # deepcode ignore unguarded~next~call: infinite counter
        config.table = f"{config.table}_{next(self.table_counter)}"
        self.store = DBTableStore(config)
        # deepcode ignore unguarded~next~call: infinite counter
        config.table = f"{config.table}_{next(self.table_counter)}"
        self.store1 = DBTableStore(config)
        # deepcode ignore unguarded~next~call: infinite counter
        config.table = f"{config.table}_{next(self.table_counter)}"
        self.store2 = DBTableStore(config)
        self.test_type: type = self.get_test_cls()
        self.value: StorableObjABC = deepcopy(self.test_type.value)
        self.value1: StorableObjABC = deepcopy(self.test_type.value1)
        self.value2: StorableObjABC = deepcopy(self.test_type.value2)
        self.key: Hashable = self.test_type.key
        self.key1: Hashable = self.test_type.key1
        self.key2: Hashable = self.test_type.key2

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down the test."""
        # db_delete(f"test_db_{_START_DB_COUNTER}", _CONFIG["database"])


if __name__ == "__main__":
    unittest.main()
