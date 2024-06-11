"""Test case for InMemoryStore class."""
import unittest
from egppy.storage.store.in_memory_store import InMemoryStore
from egppy.gc_types.ugc_class_factory import DictUGC
from egppy.gc_types.ugc_class_factory import DirtyDictUGC
from egppy.storage.store.storable_obj_abc import StorableObjABC
from tests.test_storage.store_test_base import DEFAULT_VALUES
from tests.test_storage.store_test_base import StoreTestBase


class TestInMemoryStoreDictUGC(StoreTestBase):
    """Test cases for InMemoryStore class with DictUGC.
    """
    store_type = InMemoryStore
    value_type = DictUGC
    value: StorableObjABC = DictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DictUGC(DEFAULT_VALUES[2])


class TestInMemoryStoreDirtyDictUGC(StoreTestBase):
    """Test cases for InMemoryStore class with DirtyDictUGC.
    """
    store_type = InMemoryStore
    value_type = DirtyDictUGC
    value: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[2])


class TestInMemoryStoreIntKey(StoreTestBase):
    """Test cases for InMemoryStore class with integer keys.
    """
    store_type = InMemoryStore
    value_type = DirtyDictUGC
    value: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[2])
    key = 120
    key1 = 340
    key2 = 560


if __name__ == '__main__':
    unittest.main()
