"""Test the Multi-level Caches."""
from egppy.storage.cache.user_dict_cache import UserDictCache
from egppy.storage.cache.dict_cache import DictCache
from egppy.storage.cache.cacheable_dict import CacheableDict
from egppy.storage.store.in_memory_store import InMemoryStore
from tests.test_storage.test_cache.multilevel_cache_test_base import MultilevelCacheTestBase


class TestMultiLevelCache1(MultilevelCacheTestBase):
    """Test case multilevel caches using DictCache and CacheableDicts uniformly."""
    first_level_cache_type = UserDictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict


class TestMultiLevelCache2(MultilevelCacheTestBase):
    """Test case multilevel caches using a DictCache as a first level and
    UserDictCache as a second level."""
    first_level_cache_type = DictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict
