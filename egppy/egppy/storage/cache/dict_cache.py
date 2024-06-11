"""A python dictionary based cache."""
from typing import Any, Callable
from collections.abc import Hashable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cache_illegal import CacheIllegal
from egppy.storage.cache.cache_base import CacheBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class DictCache(CacheIllegal, dict[Hashable, CacheableObjABC], CacheBase, CacheABC):  # type: ignore
    """An builtin python dictionary based fast cache.
    
    Cache is a bit of a misnomer. A DictCache is a "one-way cache", like a temporary
    store with some convinient configuration to push data to the next level. It cannot
    pull data from the next level.
    In order to use all the optimized builtin dict methods, a DictCache
    does not track access order or dirty state, it cannot support
    purging. That means it can only be of infinite size.
    """

    def __init__(self, config: CacheConfig) -> None:
        assert not config["max_items"], "DictCache can only be fast."
        dict.__init__(self)
        CacheBase.__init__(self, config=config)

    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        if _LOG_DEBUG:
            _logger.debug("DictCache: %s", str(self))
        for key, value in (x for x in self.items() if x[1].is_dirty()):
            # All GCABC objects provide a copyback method to efficiently copy back modified data.
            self.next_level.update_value(key, value.copyback())

    def flush(self) -> None:
        """Flush the cache to the next level."""
        self.copyback()
        super().clear()

    def purge(self, num: int) -> None:
        """Purge num items from the cache."""
        if num >= len(self):
            self.flush()
            return
        for _ in range(num):
            key: Hashable
            value: CacheableObjABC
            key, value = self.popitem()
            if value.is_dirty():
                self.next_level.update_value(key, value.copyback())
