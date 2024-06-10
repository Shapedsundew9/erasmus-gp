"""A python dictionary based cache."""
from typing import Any, Callable, ValuesView
from collections.abc import Hashable
from collections import UserDict
from collections.abc import MutableMapping
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cache_illegal import CacheIllegal
from egppy.storage.cache.cache_base import CacheBase
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.store.storable_obj_abc import StorableObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class UserDictCache(CacheIllegal, UserDict[Any, CacheableObjABC], CacheBase, CacheABC):
    """User dictionary based cache. A UserDict has less optimized methods 
    than a builtin dict but is more flexible and can be subclassed more easily."""

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache."""
        UserDict.__init__(self)
        CacheBase.__init__(self, config=config)

    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the cache."""
        if key not in self:
            # Need to ask the next level for the item. First check if we have space.
            self.purge_check()
            # The next level GC type must be flavored (cast) to the type stored here.
            self.data[key] = self.flavor(self.next_level[key])
        item: Any = self.data[key]
        item.touch()
        return item

    def __setitem__(self, key: Any, value: CacheableObjABC) -> None:
        """Set an item in the cache. If the cache is full make space first."""
        if key not in self:
            self.purge_check()
        item = self.flavor(value)
        self.data[key] = item
        item.touch()

    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        for key, value in (x for x in self.data.items() if x[1].is_dirty()):
            self.next_level[key] = value.copyback()

    def flush(self) -> None:
        """Flush the cache to the next level."""
        self.copyback()
        self.data.clear()

    def purge(self, num: int) -> None:
        """Purge the cache of count items."""
        if num >= len(self):
            self.flush()
            return
        victims: list[tuple[Any, int]] = sorted(
            ((k, v.seq_num()) for k, v in self.data.items()), key=_KEY)[:self.purge_count]
        for key, _ in victims:
            value: CacheableObjABC = self.data[key]
            if value.is_dirty():
                self.next_level[key] = self.data[key].copyback()
            del self.data[key]

    def purge_check(self) -> None:
        """Check if the cache needs to be purged."""
        length: int = len(self)
        if length >= self.max_items:
            assert length == self.max_items, (f"Cache length ({length}) is greater"
                f" than max_items ({self.max_items})")
            self.purge(num=self.purge_count)

    def setdefault(self, key: Hashable, default: CacheableObjABC) -> Any:
        """Set the default value for a key."""
        return self.data.setdefault(key, default)

    def update(self, m: MutableMapping[Hashable, CacheableObjABC]) -> None:  # type: ignore
        for k, v in m.items():
            self.data[k] = v

    def values(self) -> ValuesView[CacheableObjABC]:
        """Return the values of the cache."""
        return self.data.values()
