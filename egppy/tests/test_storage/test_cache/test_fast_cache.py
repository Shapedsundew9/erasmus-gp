"""Test the FastCache class."""
from egppy.storage.cache.dict_cache import DictCache as FastCache
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.gc_types.ugc_class_factory import DictUGC, DirtyDictUGC
from tests.test_storage.test_cache.fast_cache_test_base import FastCacheTestBase
from tests.test_storage.store_test_base import DEFAULT_VALUES


class TestFastCacheDictUGC(FastCacheTestBase):
    """Test case for FastCache class using DictUGC."""
    store_type = FastCache
    value_type = DictUGC
    value: StorableObjABC = DictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DictUGC(DEFAULT_VALUES[2])


class TestFastCacheDirtyDictUGC(FastCacheTestBase):
    """Test case for FastCache class using DirtyDictUGC."""
    store_type = FastCache
    value_type = DirtyDictUGC
    value: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[2])
