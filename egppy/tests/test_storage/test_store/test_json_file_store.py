"""Test case for JSONFileStore class."""
import unittest
from egppy.storage.store.json_file_store import JSONFileStore
from egppy.storage.store.storable_obj import StorableDict, StorableList, StorableSet, StorableTuple
from egppy.storage.store.storable_obj_abc import StorableObjABC
from tests.test_storage.store_test_base import DEFAULT_VALUES
from tests.test_storage.test_store.json_file_store_test_base import JSONFileStoreTestBase


class TestJSONFileStoreStorableDict(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with StorableDict."""
    store_type = JSONFileStore
    value_type = StorableDict
    value: StorableObjABC = StorableDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableDict(DEFAULT_VALUES[2])


class TestJSONFileStoreStorableList(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with StorableList."""
    store_type = JSONFileStore
    value_type = StorableList
    value: StorableObjABC = StorableList(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableList(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableList(DEFAULT_VALUES[2])


class TestJSONFileStoreStorableSet(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with StorableSet."""
    store_type = JSONFileStore
    value_type = StorableSet
    value: StorableObjABC = StorableSet(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableSet(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableSet(DEFAULT_VALUES[2])


class TestJSONFileStoreStorableTuple(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with StorableTuple."""
    store_type = JSONFileStore
    value_type = StorableTuple
    value: StorableObjABC = StorableTuple(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableTuple(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableTuple(DEFAULT_VALUES[2])


if __name__ == '__main__':
    unittest.main()
