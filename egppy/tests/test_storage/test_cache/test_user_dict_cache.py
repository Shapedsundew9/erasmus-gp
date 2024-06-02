"""Test the UserDictCache class."""
from egppy.storage.cache.cache_class_factory import UserDictCache
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.gc_types.ugc_class_factory import DictUGC, DirtyDictUGC
from tests.test_storage.test_cache.cache_test_base import CacheTestBase
from tests.test_storage.store_test_base import DEFAULT_VALUES


class TestUserDictCacheDictUGC(CacheTestBase):
    """Test case for UserDictCache class using DictUGC."""
    store_type = UserDictCache
    value_type = DictUGC
    value: StorableObjABC = DictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DictUGC(DEFAULT_VALUES[2])


class TestUserDictCacheDirtyDictUGC(CacheTestBase):
    """Test case for UserDictCache class using DictUGC."""
    store_type = UserDictCache
    value_type = DirtyDictUGC
    value: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[0])
    value1: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[1])
    value2: StorableObjABC = DirtyDictUGC(DEFAULT_VALUES[2])
