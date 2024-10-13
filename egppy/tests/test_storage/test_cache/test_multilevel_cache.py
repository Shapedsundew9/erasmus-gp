"""Test the Multi-level Caches."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.cache.cache import DictCache
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict, CacheableDirtyList
from egppy.storage.cache.cacheable_obj import CacheableDict, CacheableList
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.dirty_cache import DirtyDictCache
from egppy.storage.store.in_memory_store import InMemoryStore
from tests.test_storage.test_cache.multilevel_cache_test_base import (
    SECOND_LEVEL_CACHE_SIZE,
    MultilevelCacheTestBase,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestMultiLevelCache11(MultilevelCacheTestBase):
    """Test case multilevel caches using DictCache and CacheableDicts uniformly."""

    first_level_cache_type = DictCache
    second_level_cache_type = DictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict


class TestMultiLevelCache12(MultilevelCacheTestBase):
    """Test case multilevel caches using DictCache and CacheableDirtyDicts uniformly."""

    first_level_cache_type = DictCache
    second_level_cache_type = DictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyDict
    second_level_value_type = CacheableDirtyDict
    store_value_type = CacheableDirtyDict


class TestMultiLevelCache13(MultilevelCacheTestBase):
    """Test case multilevel caches using DictCache and CacheableLists uniformly."""

    first_level_cache_type = DictCache
    second_level_cache_type = DictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableList
    second_level_value_type = CacheableList
    store_value_type = CacheableList

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type((i,)) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]


class TestMultiLevelCache14(MultilevelCacheTestBase):
    """Test case multilevel caches using DictCache and CacheableDirtyLists uniformly."""

    first_level_cache_type = DictCache
    second_level_cache_type = DictCache
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
    DictCache as a second level with CacheableDicts."""

    first_level_cache_type = DirtyDictCache
    second_level_cache_type = DictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict


class TestMultiLevelCache22(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    DictCache as a second level with CacheableDirtyDicts."""

    first_level_cache_type = DirtyDictCache
    second_level_cache_type = DictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyDict
    second_level_value_type = CacheableDirtyDict
    store_value_type = CacheableDirtyDict


class TestMultiLevelCache23(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    DictCache as a second level with CacheableLists."""

    first_level_cache_type = DirtyDictCache
    second_level_cache_type = DictCache
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
    DictCache as a second level with CacheableDirtyLists."""

    first_level_cache_type = DirtyDictCache
    second_level_cache_type = DictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDirtyList
    second_level_value_type = CacheableDirtyList
    store_value_type = CacheableDirtyList

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type((i,)) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]
