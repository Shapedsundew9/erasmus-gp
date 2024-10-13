"""Cache Base Abstract Base Class"""

from abc import abstractmethod
from typing import TypedDict

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.store_abc import StoreABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheConfig(TypedDict):
    """Cache configuration."""

    max_items: int  # Maximum number of items in the cache. 0 = infinite
    purge_count: int  # Number of items to purge when the cache is full
    next_level: StoreABC  # The next level of caching or storage
    flavor: type[CacheableObjABC]  # The type of item stored in the cache


class CacheABC(StoreABC):
    """Abstract class for cache base classes.

    The cache class must implement all the primitives of cache operations.
    """

    @abstractmethod
    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache configuration."""
        # These unused definitions prevent pylance from complaining about missing attributes
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        self.flavor: type[StorableObjABC] = config["flavor"]
        raise NotImplementedError("CacheABC.__init__ must be overridden")

    @abstractmethod
    def copyback(self) -> None:
        """Copy the cache back to the next level.
        Copy all dirty items back to the next level store. No purge or flush
        is done and the state of the cache and all access sequence numbers are
        left unchanged.
        """
        raise NotImplementedError("copy_back must be overridden")

    @abstractmethod
    def copythrough(self) -> None:
        """Copy the cache through all the way to the store.
        Copy all dirty items in the cache back to the store (through multiple cache levels).
        No purge or flush is done, all items are marked clean and all access sequence numbers
        are left unchanged.
        NOTE: If the next level cache has dirty items they will be copied back to the store too.
        """
        raise NotImplementedError("copythrough must be overridden")

    @abstractmethod
    def flush(self) -> None:
        """Flush the cache.
        A flush is semantically a copyback() followed by a clear().
        """
        raise NotImplementedError("flush must be overridden")

    @abstractmethod
    def purge(self, num: int) -> None:
        """Purge the cache of num items.
        The items purged are the least recently used items (as defined by the
        access sequence number). If an item is dirty, it must be copied back to
        the next level store before it is purged.
        num may be greater than or euqal to the number of items in the cache in
        which case purge() behaves like flush() (which may be an optimisation).
        """
        raise NotImplementedError("purge must be overridden")
