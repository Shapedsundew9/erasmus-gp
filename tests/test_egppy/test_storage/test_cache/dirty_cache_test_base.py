"""Dirty cache test base class."""

from json import load
from os.path import dirname, join

from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cacheable_obj import CacheableDict
from egppy.storage.cache.dirty_cache import DirtyDictCache
from egppy.storage.store.json_file_store import JSONFileStore
from tests.test_egppy.test_storage.store_test_base import StoreTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Number of items to put in the cache for testing
NUM_CACHE_ITEMS = 5


class DirtyCacheTestBase(StoreTestBase):
    """Cache test base class."""

    json_data: list[dict]
    store_type = DirtyDictCache
    cache_config: CacheConfig = {
        "max_items": 0,
        "purge_count": 0,
        "next_level": JSONFileStore(CacheableDict),
        "flavor": CacheableDict,
    }

    @classmethod
    def get_cache_cls(cls) -> type[CacheABC]:
        """Get the Store class."""
        assert issubclass(cls.store_type, CacheABC)
        return cls.store_type

    def setUp(self) -> None:
        self.cache_type: type[CacheABC] = self.get_cache_cls()
        self.cache = self.cache_type(config=DirtyCacheTestBase.cache_config)
        self.cache1 = self.cache_type(config=DirtyCacheTestBase.cache_config)
        self.cache2 = self.cache_type(config=DirtyCacheTestBase.cache_config)
        # Store test base class test methods use the store* members
        self.store: CacheABC = self.cache
        self.store1: CacheABC = self.cache1
        self.store2: CacheABC = self.cache2
        # The next level store for the caches is persistent so need to make sure they
        # are empty before each test.
        self.cache.next_level.clear()
        self.cache1.next_level.clear()
        self.cache2.next_level.clear()

    @classmethod
    def setUpClass(cls) -> None:
        datafile: str = join(dirname(p=__file__), "..", "data", "ugc_test_data.json")
        with open(file=datafile, mode="r", encoding="utf-8") as file:
            cls.json_data: list[dict] = load(fp=file)

    def test_copyback(self) -> None:
        """Test the copyback method."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item["signature"]] = CacheableDict(item)
        # Nothing has been pushed to store yet
        self.assertFalse(expr=len(self.cache.next_level))
        self.cache.copyback()
        # All items are in the store
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            stored_item = self.cache.next_level[item["signature"]]
            self.assertEqual(first=CacheableDict(stored_item), second=CacheableDict(item))

    def test_flush(self) -> None:
        """Test the flush method."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item["signature"]] = CacheableDict(item)
        self.cache.flush()
        # Nothing put in the cache is still there
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.assertNotIn(member=item["signature"], container=self.cache)
        self.assertFalse(expr=len(self.cache))  # Cache is empty
        # All items are in the store
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            stored_item = self.cache.next_level[item["signature"]]
            self.assertEqual(first=CacheableDict(stored_item), second=CacheableDict(item))

    def test_purge(self) -> None:
        """purge method is not supported for dict caches."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item["signature"]] = CacheableDict(item)
        self.cache.purge(num=1)
        self.assertEqual(first=len(self.cache), second=NUM_CACHE_ITEMS - 1)

    def test_touch(self) -> None:
        """Test the touch method."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item["signature"]] = CacheableDict(item)
        # In a dict cache the touch method has no real use case
        self.cache[self.json_data[0]["signature"]].touch()
