"""Test case for JSONFileStore class."""
import unittest
from egppy.storage.store.json_file_store import JSONFileStore
from egppy.gc_types.ugc_class_factory import DictUGC
from egppy.gc_types.ugc_class_factory import DirtyDictUGC
from egppy.storage.store.storable_obj_abc import StorableObjABC
from tests.test_storage.store_test_base import DEFAULT_VALUES
from tests.test_storage.test_store.json_file_store_test_base import JSONFileStoreTestBase


class TestJSONFileStoreDictUGC(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with DictUGC.
    """
    store_type = JSONFileStore
    value_type = DictUGC
    value: StorableObjABC = DictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DictUGC(DEFAULT_VALUES[2])


class TestJSONFileStoreDirtyDictUGC(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with DirtyDictUGC.
    """
    store_type = JSONFileStore
    value_type = DirtyDictUGC
    value: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[2])


class TestJSONFileStoreIntKey(JSONFileStoreTestBase):
    """Test cases for JSONFileStore class with integer keys.
    """
    store_type = JSONFileStore
    value_type = DirtyDictUGC
    value: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[2])
    key = 120
    key1 = 340
    key2 = 560


if __name__ == '__main__':
    unittest.main()
