"""A python dictionary based cache."""
from typing import Any, Callable, Hashable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
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


class DictCache(dict[Hashable, CacheableObjABC], CacheABC):
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
        self.next_level: StoreABC = config["next_level"]
        super().__init__()

    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        for key, value in filter(lambda x: x[1].is_dirty(), self.items()):
            # All GCABC objects provide a copyback method to efficiently copy back modified data.
            self.next_level[key] = value.copyback()

    def flush(self) -> None:
        """Flush the cache to the next level."""
        self.copyback()
        super().clear()

    def purge(self, num: int) -> None:
        """Illegal method."""
        assert False, "FastCache does not support purging."

    def touch(self, key: Hashable) -> None:
        """No-op for a FastCache."""
        assert False, "FastCache should not be touched."
