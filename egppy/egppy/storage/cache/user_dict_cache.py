"""A python dictionary based cache."""
from typing import Any, Callable
from collections.abc import Hashable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cache_base import CacheBase
from egppy.storage.cache.cache_mixin import CacheMixin
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class UserDictCache(CacheBase, CacheMixin, CacheABC):
    """User dictionary based cache. A UserDict has less optimized methods 
    than a builtin dict but is more flexible and can be subclassed more easily."""

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache."""
        super().__init__(config=config)
        self.data: dict[Hashable, CacheableObjABC] = {}

    def __len__(self) -> int:
        """Return the number of items in the cache."""
        return len(self.data)

    def __contains__(self, key: Hashable) -> bool:
        """Check if the cache contains a key."""
        return key in self.data

    def __delitem__(self, key: Hashable) -> None:
        """Delete an item from the cache."""
        value: CacheableObjABC = self.data[key]
        if value.is_dirty():
            self.next_level[key] = value
        del self.data[key]

    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the cache."""
        if _LOG_DEBUG:
            _logger.debug("UserDictCache getitem: %s", str(key))
        if key not in self:
            if _LOG_DEBUG:
                _logger.debug("UserDictCache getitem: %s not in cache.", str(key))
            # Need to ask the next level for the item. First check if we have space.
            self.purge_check()
            # The next level object type must be flavored (cast) to the type stored here.
            value = self.next_level[key]
            self.data[key] = self.flavor(value) if self._convert else value  # type: ignore
        item: CacheableObjABC = self.data[key]
        item.touch()
        return item

    def __setitem__(self, key: Any, value: CacheableObjABC) -> None:
        """Set an item in the cache. If the cache is full make space first."""
        if key not in self:
            self.purge_check()
        item = self.flavor(value) if not isinstance(value, self.flavor) else value
        self.data[key] = item  # type: ignore
        item.touch()  # type: ignore
        if _LOG_DEBUG:
            _logger.debug("UserDictCache setitem: %s: %s", str(key), str(item))

    def purge(self, num: int) -> None:
        """Purge the cache of count items."""
        if num >= len(self):
            self.flush()
            return
        victims: list[tuple[Any, int]] = sorted(
            ((k, v.seq_num()) for k, v in self.data.items()), key=_KEY)[:self.purge_count]
        if _LOG_DEBUG:
            _logger.debug("UserDictCache purge %d items.", len(victims))
        for key, _ in victims:
            del self[key]
