"""Test Store classes."""
from __future__ import annotations
import unittest
from random import choices
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.in_memory_store import InMemoryStore
from egppy.storage.cache.cacheable_dict import CacheableDict
from egppy.storage.cache.user_dict_cache import UserDictCache
from egppy.storage.cache.dict_cache import DictCache
from egppy.storage.cache.cache_abc import CacheABC
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC


# Log base 2 second level cache size
LOG2_SECOND_LEVEL_CACHE_SIZE: int = 4

FIRST_LEVEL_CACHE_SIZE: int = 2**(LOG2_SECOND_LEVEL_CACHE_SIZE - 1)
SECOND_LEVEL_CACHE_SIZE: int = 2**LOG2_SECOND_LEVEL_CACHE_SIZE


class MultilevelCacheTestBase(unittest.TestCase):
    """Test case for multilevel cache classes."""

    # The Store class to test. Override this in subclasses.
    first_level_cache_type = UserDictCache
    second_level_cache_type = UserDictCache
    store_type = InMemoryStore
    # The Value class to test. Override this in subclasses.
    first_level_value_type = CacheableDict
    second_level_value_type = CacheableDict
    store_value_type = CacheableDict

    @classmethod
    def get_test_cls(cls) -> type:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith('TestBase')

    @classmethod
    def get_first_level_cache_cls(cls) -> type[CacheABC]:
        """Get the first level cache class."""
        return cls.first_level_cache_type

    @classmethod
    def get_second_level_cache_cls(cls) -> type[CacheABC]:
        """Get the first level cache class."""
        return cls.second_level_cache_type

    @classmethod
    def get_store_cls(cls) -> type[StoreABC]:
        """Get the Store class."""
        return cls.store_type

    @classmethod
    def get_first_level_value_cls(cls) -> type[CacheableObjABC]:
        """Get the Value class."""
        return cls.first_level_value_type

    @classmethod
    def get_second_level_value_cls(cls) -> type[CacheableObjABC]:
        """Get the Value class."""
        return cls.second_level_value_type

    @classmethod
    def get_store_value_cls(cls) -> type[StorableObjABC]:
        """Get the Value class."""
        return cls.store_value_type

    @classmethod
    def set_values(cls, value_type: type[CacheableObjABC]) -> list[CacheableObjABC]:
        """Set the values to be used in the tests."""
        return [value_type({"value": i}) for i in range(2 * SECOND_LEVEL_CACHE_SIZE)]

    def setUp(self) -> None:
        """Set up for each test."""
        self.store = self.get_store_cls()(self.get_store_value_cls())
        self.second_level_cache = self.get_second_level_cache_cls()({
            "max_items": SECOND_LEVEL_CACHE_SIZE,
            "purge_count": SECOND_LEVEL_CACHE_SIZE // 2,
            "next_level": self.store,
            "flavor": self.get_second_level_value_cls()
        })
        flc_type = self.get_first_level_cache_cls()
        self.first_level_cache = flc_type({
            "max_items": FIRST_LEVEL_CACHE_SIZE if flc_type is not DictCache else 0, 
            "purge_count": FIRST_LEVEL_CACHE_SIZE // 2 if flc_type is not DictCache else 0,
            "next_level": self.second_level_cache,
            "flavor": self.get_first_level_value_cls()
        })
        self.values = self.set_values(self.get_first_level_value_cls())

    def test_readback(self) -> None:
        """Test writing 2x the 2nd level cache size and reading back."""
        if self.running_in_test_base_class():
            return
        for v in self.values:
            self.first_level_cache[v['value']] = v
        # DictCache does not automatically copyback()
        if self.get_first_level_cache_cls() is DictCache:
            self.first_level_cache.copyback()
        # Do not check the first level cache as it may be a DictCache
        # The second level cache should be full
        self.assertEqual(first=len(self.second_level_cache), second=SECOND_LEVEL_CACHE_SIZE)
        # The store should have the items from the second level cache that were purged
        # That is the first half of the values
        self.assertEqual(first=len(self.store), second=SECOND_LEVEL_CACHE_SIZE)
        # Reading back through the first level cache should bring the items back from the
        # second level cache and store. This causes the newest itemes to be purged back
        # if not a DictCache.
        for v in self.values:
            self.assertEqual(first=self.first_level_cache[v['value']], second=v)
        # To get everything in the store when using a DictCache, the copythrough() method
        # must be called.
        if self.get_first_level_cache_cls() is DictCache:
            self.first_level_cache.copythrough()
        # The store should have all the items
        self.assertEqual(first=len(self.store), second=2 * SECOND_LEVEL_CACHE_SIZE)

    def test_interleved_readback(self) -> None:
        """Test interleaved writing and reading back."""
        if self.running_in_test_base_class():
            return
        for i in range(LOG2_SECOND_LEVEL_CACHE_SIZE + 2):
            for v in range(2**i // 2, 2**i):
                self.first_level_cache[v] = self.values[v]
            # DictCache does not automatically copyback()
            if self.get_first_level_cache_cls() is DictCache:
                self.first_level_cache.copyback()
            for v in range(2**i // 4, 2**i // 2):
                self.assertEqual(first=self.first_level_cache[v], second=self.values[v])
        for v in range(2 * SECOND_LEVEL_CACHE_SIZE):
            self.assertEqual(first=self.first_level_cache[v], second=self.values[v])
        self.assertEqual(first=len(self.second_level_cache), second=SECOND_LEVEL_CACHE_SIZE)
        # To get everything in the store when using a DictCache, the copythrough() method
        # must be called.
        if self.get_first_level_cache_cls() is DictCache:
            self.first_level_cache.copythrough()
        self.assertEqual(first=len(self.store), second=2 * SECOND_LEVEL_CACHE_SIZE)

    def test_random_readback(self) -> None:
        """Test random writing and reading back."""
        if self.running_in_test_base_class():
            return
        for v in self.values:
            self.first_level_cache[v['value']] = v
        # DictCache does not automatically copyback()
        if self.get_first_level_cache_cls() is DictCache:
            self.first_level_cache.copyback()
        for v in choices(self.values, k = 4 * SECOND_LEVEL_CACHE_SIZE):
            self.assertEqual(first=self.first_level_cache[v['value']], second=v)
        # To get everything in the store when using a DictCache, the copythrough() method
        # must be called.
        if self.get_first_level_cache_cls() is DictCache:
            self.first_level_cache.copythrough()
        self.assertEqual(first=len(self.store), second=2 * SECOND_LEVEL_CACHE_SIZE)
