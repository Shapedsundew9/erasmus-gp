"""Test case for InMemoryStore class."""
import unittest
from egppy.storage.store.in_memory_store import InMemoryStore
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.storable_obj import StorableDict, StorableList, StorableSet, StorableTuple
from tests.test_storage.store_test_base import DEFAULT_VALUES
from tests.test_storage.store_test_base import StoreTestBase


class TestInMemoryStoreStorableDict(StoreTestBase):
    """Test cases for InMemoryStore class with StorableDict."""
    store_type = InMemoryStore
    value_type = StorableDict
    value: StorableObjABC = StorableDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableDict(DEFAULT_VALUES[2])


class TestInMemoryStoreStorableList(StoreTestBase):
    """Test cases for InMemoryStore class with StorableList."""
    store_type = InMemoryStore
    value_type = StorableList
    value: StorableObjABC = StorableList(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableList(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableList(DEFAULT_VALUES[2])


class TestInMemoryStoreStorableSet(StoreTestBase):
    """Test cases for InMemoryStore class with StorableSet."""
    store_type = InMemoryStore
    value_type = StorableSet
    value: StorableObjABC = StorableSet(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableSet(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableSet(DEFAULT_VALUES[2])


class TestInMemoryStoreStorableTuple(StoreTestBase):
    """Test cases for InMemoryStore class with StorableTuple."""
    store_type = InMemoryStore
    value_type = StorableTuple
    value: StorableObjABC = StorableTuple(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableTuple(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableTuple(DEFAULT_VALUES[2])


class TestInMemoryStoreIntKey(StoreTestBase):
    """Test cases for InMemoryStore class with integer keys.
    """
    store_type = InMemoryStore
    value_type = StorableList
    value: StorableObjABC = StorableList(DEFAULT_VALUES[0])
    value1: StorableObjABC = StorableList(DEFAULT_VALUES[1])
    value2: StorableObjABC = StorableList(DEFAULT_VALUES[2])
    key = 120
    key1 = 340
    key2 = 560


if __name__ == '__main__':
    unittest.main()
