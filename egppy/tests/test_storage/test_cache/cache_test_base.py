"""Cache test base class."""
from logging import Logger, NullHandler, getLogger, DEBUG
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.store.json_file_store import JSONFileStore
from egppy.storage.cache.user_dict_cache import UserDictCache
from egppy.gc_types.ugc_class_factory import DictUGC
from tests.test_storage.test_cache.fast_cache_test_base import FastCacheTestBase, NUM_CACHE_ITEMS


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


# Maximum number of items the cache can hold
MAX_NUM_CACHE_ITEMS = 2 * NUM_CACHE_ITEMS
NUM_CACHE_PURGE_ITEMS = NUM_CACHE_ITEMS  # i.e. 50%


class CacheTestBase(FastCacheTestBase):
    """Cache test base class."""
    store_type = UserDictCache
    cache_config: CacheConfig = {
        "max_items": MAX_NUM_CACHE_ITEMS,
        "purge_count": NUM_CACHE_PURGE_ITEMS,
        "next_level": JSONFileStore(),
        "flavor": DictUGC
    }

    @classmethod
    def get_cache_cls(cls) -> type[CacheABC]:
        """Get the Store class."""
        assert issubclass(cls.store_type, CacheABC)
        return cls.store_type

    def setUp(self) -> None:
        self.cache_type: type[CacheABC] = self.get_cache_cls()
        self.cache = self.cache_type(config=CacheTestBase.cache_config)
        self.cache1 = self.cache_type(config=CacheTestBase.cache_config)
        self.cache2 = self.cache_type(config=CacheTestBase.cache_config)
        # Store test base class test methods use the store* members
        self.store: CacheABC = self.cache
        self.store1: CacheABC = self.cache1
        self.store2: CacheABC = self.cache2
        # The next level store for the caches is persistent so need to make sure they
        # are empty before each test.
        self.cache.next_level.clear()  # Disables below for a possible pylint bug
        self.cache1.next_level.clear()  # pylint: disable=no-member
        self.cache2.next_level.clear()  # pylint: disable=no-member

    def test_get_from_next_level(self) -> None:
        """Test getting an item from the next level."""
        if self.running_in_test_base_class():
            return
        # Add an item to the next level
        item = self.json_data[0]
        self.cache.next_level[item['signature']] = DictUGC(item)
        # Get the item from the cache
        self.assertEqual(first=self.cache[item['signature']], second=DictUGC(item))

    def test_purge(self) -> None:
        """Purge method is called by over filling the cache."""
        if self.running_in_test_base_class():
            return
        # Overfill the cache by one item to trigger a purge
        for item in self.json_data[:MAX_NUM_CACHE_ITEMS + 1]:
            self.cache[item['signature']] = DictUGC(item)
        post_num = MAX_NUM_CACHE_ITEMS + 1 - NUM_CACHE_PURGE_ITEMS
        self.assertEqual(first=len(self.cache), second=post_num)
        # The cache should have purged the oldest items
        for item in self.json_data[:NUM_CACHE_PURGE_ITEMS]:
            self.assertNotIn(member=item['signature'], container=self.cache)
        # The cache should have the newest items
        for item in self.json_data[NUM_CACHE_PURGE_ITEMS:MAX_NUM_CACHE_ITEMS + 1]:
            self.assertIn(member=item['signature'], container=self.cache)
        # The store should have the purged items
        for item in self.json_data[:NUM_CACHE_PURGE_ITEMS]:
            self.assertIn(member=item['signature'], container=self.cache.next_level)

    def test_touch(self) -> None:
        """Test the touch method."""
        if self.running_in_test_base_class():
            return
        # Exactly fill the cache with items
        for item in self.json_data[:MAX_NUM_CACHE_ITEMS]:
            self.cache[item['signature']] = DictUGC(item)
        # Touch the first item
        self.cache[self.json_data[0]['signature']].touch()
        # Add another item to the cache causing a purge
        item = self.json_data[MAX_NUM_CACHE_ITEMS]
        self.cache[item['signature']] = DictUGC(item)
        # The first item should still be in the cache
        self.assertIn(member=self.json_data[0]['signature'], container=self.cache)
