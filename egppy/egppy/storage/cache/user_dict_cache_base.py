"""A python dictionary based cache."""
from typing import Any, Callable, Type
from logging import Logger, NullHandler, getLogger, DEBUG
from itertools import count
from collections import UserDict
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.gc_types.gc_abc import GCABC
from egppy.storage.store.store_abc import StoreABC


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class UserDictCacheBase(UserDict[Any, GCABC], CacheABC):
    """User dictionary based cache. A UserDict has less optimized methods 
    than a builtin dict but is more flexible and can be subclassed more easily."""

    def __init__(self, config: CacheConfig) -> None:
        self.access_counter = count()
        self.seqnum: dict[Any, int] = {}
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        self.flavor: Type[GCABC] = config["flavor"]
        super().__init__()

    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        for key, value in filter(lambda x: x[1].is_dirty(), self.items()):
            self.next_level[key] = value

    def flush(self) -> None:
        """Flush the cache to the next level."""
        self.copyback()
        super().clear()

    def purge(self, num: int) -> None:
        """Purge the cache of count items."""
        victims: list[tuple[Any, int]] = sorted(self.seqnum.items(), key=_KEY)[:self.purge_count]
        for key, _ in victims:
            value: GCABC = self[key]
            if value.is_dirty():
                self.next_level[key] = self[key].copyback()
            del self[key]

    def touch(self, key: Any) -> None:
        """Touch the cache item to update the access sequence number."""
        self.seqnum[key] = next(self.access_counter)
