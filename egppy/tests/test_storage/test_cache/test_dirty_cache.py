"""Test the DirtyDictCache class."""
from egppy.storage.cache.dirty_cache import DirtyDictCache
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.cache.cacheable_obj import CacheableDict
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from tests.test_storage.test_cache.dirty_cache_test_base import DirtyCacheTestBase
from tests.test_storage.store_test_base import DEFAULT_VALUES


class TestDirtyDictCacheCacheableDict(DirtyCacheTestBase):
    """Test case for DirtyDictCache class using CacheableDict."""
    store_type = DirtyDictCache
    value_type = CacheableDict
    value: StorableObjABC = CacheableDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = CacheableDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = CacheableDict(DEFAULT_VALUES[2])


class TestDirtyDictCacheCacheableDirtyDict(DirtyCacheTestBase):
    """Test case for DirtyDictCache class using CacheableDirtyDict."""
    store_type = DirtyDictCache
    value_type = CacheableDirtyDict
    value: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[2])
