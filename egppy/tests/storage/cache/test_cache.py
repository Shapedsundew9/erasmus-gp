"""Unit tests for the cache modules."""
import unittest
from egppy.storage.cache.cache_factory import cache_factory
from egppy.storage.cache.user_dict_cache import UserDictCacheBase
from egppy.storage.cache.dict_cache import DictCache
from egppy.storage.store.json_file_store import JsonFileStore
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig


class TestCache(unittest.TestCase):
    """Test case for the cache modules."""

    def setUp(self) -> None:
        """Set up the test case."""
        remote_cache_client_config: CacheConfig = {
            "max_items": 0,
            "purge_count": 0,
            "next_level": JsonFileStore(file_path="genetic_code_store.json")
        }

        compact_cache_config: CacheConfig = {
            "max_items": 100000,
            "purge_count": 25000,
            "next_level": cache_factory(cls=UserDictCacheBase, config=remote_cache_client_config)
        }

        fast_cache_config: CacheConfig = {
            "max_items": 0,
            "purge_count": 0,
            "next_level": cache_factory(cls=UserDictCacheBase, config=compact_cache_config)
        }
        self.genetic_code_cache: CacheABC = cache_factory(cls=DictCache, config=fast_cache_config)

