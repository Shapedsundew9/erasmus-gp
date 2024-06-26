"""Test the Multi-level Caches."""
from egppy.storage.cache.user_dict_cache import UserDictCache
from egppy.storage.cache.dict_cache import DictCache
from egppy.storage.cache.cacheable_dict import CacheableDict
from egppy.storage.cache.cacheable_dirty_dict import CacheableDirtyDict
from egppy.storage.cache.cacheable_dirty_list import CacheableDirtyList
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_list import CacheableList
from egppy.storage.store.in_memory_store import InMemoryStore
from tests.test_storage.test_cache.multilevel_cache_test_base import (
    MultilevelCacheTestBase, SECOND_LEVEL_CACHE_SIZE)


class TestMultiLevelCache11(MultilevelCacheTestBase):
    """Test case multilevel caches using UserDictCache and CacheableDicts uniformly."""
    first_level_cache_type = UserDictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict


class TestMultiLevelCache12(MultilevelCacheTestBase):
    """Test case multilevel caches using UserDictCache and CacheableDirtyDicts uniformly."""
    first_level_cache_type = UserDictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyDict
    second_level_value_type = CacheableDirtyDict
    store_value_type = CacheableDirtyDict


class TestMultiLevelCache13(MultilevelCacheTestBase):
    """Test case multilevel caches using UserDictCache and CacheableLists uniformly."""
    first_level_cache_type = UserDictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableList
    second_level_value_type = CacheableList
    store_value_type = CacheableList

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type((i,)) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]


class TestMultiLevelCache14(MultilevelCacheTestBase):
    """Test case multilevel caches using UserDictCache and CacheableDirtyLists uniformly."""
    first_level_cache_type = UserDictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyList
    second_level_value_type = CacheableDirtyList
    store_value_type = CacheableDirtyList

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type((i,)) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]


class TestMultiLevelCache21(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    UserDictCache as a second level with CacheableDicts."""
    first_level_cache_type = DictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict


class TestMultiLevelCache22(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    UserDictCache as a second level with CacheableDirtyDicts."""
    first_level_cache_type = DictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyDict
    second_level_value_type = CacheableDirtyDict
    store_value_type = CacheableDirtyDict


class TestMultiLevelCache23(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    UserDictCache as a second level with CacheableLists."""
    first_level_cache_type = DictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableList
    second_level_value_type = CacheableList
    store_value_type = CacheableList

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type((i,)) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]


class TestMultiLevelCache24(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    UserDictCache as a second level with CacheableDirtyLists."""
    first_level_cache_type = DictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyList
    second_level_value_type = CacheableDirtyList
    store_value_type = CacheableDirtyList

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type((i,)) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]
