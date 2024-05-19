"""A python dictionary based cache."""
from typing import Any, Callable
from itertools import count
from collections import UserDict
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.types.gc_abc import GCABC
from egppy.storage.store.store_abc import StoreABC


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class UserDictCache(UserDict[Any, GCABC], CacheABC):
    """Dictionary based cache store."""

    def __init__(self, config: CacheConfig) -> None:
        self.access_counter = count()
        self.seqnum: dict[Any, int] = {}
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        super().__init__()

    def copy_back(self) -> None:
        """Copy the cache back to the next level."""
        for key, value in filter(lambda x: x[1].is_dirty(), self.items()):
            self.next_level[key] = value

    def flush(self) -> None:
        """Flush the cache to the next level."""
        self.copy_back()
        super().clear()

    def purge(self, num: int) -> None:
        """Purge the cache of count items."""
        victims: list[tuple[Any, int]] = sorted(self.seqnum.items(), key=_KEY)[:self.purge_count]
        for key, _ in victims:
            value: GCABC = self[key]
            if value.is_dirty():
                self.next_level[key] = self[key]
            del self[key]

    def touch(self, key: Any) -> None:
        """Touch the cache item to update the access sequence number."""
        self.seqnum[key] = next(self.access_counter)
