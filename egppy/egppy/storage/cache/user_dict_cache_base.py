"""A python dictionary based cache."""
from typing import Any, Callable, Hashable
from itertools import count
from collections import UserDict
from collections.abc import MutableMapping
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_types.null_gc import NULL_GC
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.store.store_abc import StoreABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class UserDictCacheBase(UserDict[Any, CacheableObjABC], CacheABC):
    """User dictionary based cache. A UserDict has less optimized methods 
    than a builtin dict but is more flexible and can be subclassed more easily."""

    def __init__(self, config: CacheConfig) -> None:
        self.access_counter = count()
        self.seqnum: dict[Any, int] = {}
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        self.flavor: type[CacheableObjABC] = config["flavor"]
        super().__init__()

    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        for key, value in (x for x in self.items() if x[1].is_dirty()):
            self.next_level[key] = value

    def flush(self) -> None:
        """Flush the cache to the next level."""
        self.copyback()
        for key in tuple(self.keys()):
            super().__delitem__(key)

    def purge(self, num: int) -> None:
        """Purge the cache of count items."""
        if num >= len(self):
            self.flush()
            return
        victims: list[tuple[Any, int]] = sorted(self.seqnum.items(), key=_KEY)[:self.purge_count]
        for key, _ in victims:
            value: CacheableObjABC = self[key]
            if value.is_dirty():
                self.next_level[key] = self[key].copyback()
            super().__delitem__(key)

    def setdefault(self, key: Hashable, default: CacheableObjABC = NULL_GC) -> Any:  # type: ignore
        if key in self:
            return self[key]
        self[key] = default
        return default

    def touch(self, key: Hashable) -> None:
        """Touch the cache item to update the access sequence number."""
        # deepcode ignore unguarded~next~call: access_counter cannot raise StopIteration. Infinite sequence.
        self.seqnum[key] = next(self.access_counter)

    def update(self, m: MutableMapping[Hashable, CacheableObjABC]) -> None:  # type: ignore
        for k, v in m.items():
            self[k] = v
