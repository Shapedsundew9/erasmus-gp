"""Fast cache test base class."""
from os.path import join, dirname
from json import load
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.store.json_file_store import JSONFileStore
from egppy.storage.cache.dict_cache import DictCache
from egppy.gc_types.ugc_class_factory import DictUGC
from tests.test_storage.store_test_base import StoreTestBase


# Number of items to put in the cache for testing
NUM_CACHE_ITEMS = 5


class FastCacheTestBase(StoreTestBase):
    """Cache test base class."""
    json_data: list[dict]
    store_type = DictCache
    cache_config: CacheConfig = {
        "max_items": 0,
        "purge_count": 0,
        "next_level": JSONFileStore(DictUGC),
        "flavor": DictUGC
    }

    @classmethod
    def get_cache_cls(cls) -> type[CacheABC]:
        """Get the Store class."""
        assert issubclass(cls.store_type, CacheABC)
        return cls.store_type

    @classmethod
    def setUpClass(cls) -> None:
        datafile: str = join(dirname(p=__file__), '..', 'data', 'ugc_test_data.json')
        with open(file=datafile, mode='r', encoding='utf-8') as file:
            cls.json_data: list[dict] = load(fp=file)

    def setUp(self) -> None:
        self.cache_type: type[CacheABC] = self.get_cache_cls()
        self.cache = self.cache_type(config=FastCacheTestBase.cache_config)
        self.cache1 = self.cache_type(config=FastCacheTestBase.cache_config)
        self.cache2 = self.cache_type(config=FastCacheTestBase.cache_config)
        # Store test base class test methods use the store* members
        self.store: CacheABC = self.cache
        self.store1: CacheABC = self.cache1
        self.store2: CacheABC = self.cache2
        # The next level store for the caches is persistent so need to make sure they
        # are empty before each test.
        self.cache.next_level.clear()
        self.cache1.next_level.clear()
        self.cache2.next_level.clear()

    def test_copyback(self) -> None:
        """Test the copyback method."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item['signature']] = DictUGC(item)
        self.assertFalse(expr=len(self.cache.next_level))  # Nothing has been pushed to store yet
        self.cache.copyback()
        for item in self.json_data[:NUM_CACHE_ITEMS]:  # All items are in the store
            stored_item = self.cache.next_level[item['signature']]
            self.assertEqual(first=DictUGC(stored_item), second=DictUGC(item))

    def test_flush(self) -> None:
        """Test the flush method."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item['signature']] = DictUGC(item)
        self.cache.flush()
        for item in self.json_data[:NUM_CACHE_ITEMS]:  # Nothing put in the cache is still there
            self.assertNotIn(member=item['signature'], container=self.cache)
        self.assertFalse(expr=len(self.cache))  # Cache is empty
        for item in self.json_data[:NUM_CACHE_ITEMS]:  # All items are in the store
            stored_item = self.cache.next_level[item['signature']]
            self.assertEqual(first=DictUGC(stored_item), second=DictUGC(item))

    def test_purge(self) -> None:
        """purge method is not supported for dict caches."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item['signature']] = DictUGC(item)
        self.cache.purge(num=1)
        self.assertEqual(first=len(self.cache), second=NUM_CACHE_ITEMS-1)

    def test_touch(self) -> None:
        """Test the touch method."""
        if self.running_in_test_base_class():
            return
        for item in self.json_data[:NUM_CACHE_ITEMS]:
            self.cache[item['signature']] = DictUGC(item)
        # In a dict cache the touch method has no real use case
        self.cache[self.json_data[0]['signature']].touch()
