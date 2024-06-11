"""Cache Base Abstract Base Class"""
from typing import Any, TypedDict
from collections.abc import Hashable
from abc import abstractmethod
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_illegal import StoreIllegal
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC


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


def validate_cache_config(config: CacheConfig) -> None:
    """Validate the cache configuration."""
    if not isinstance(config["max_items"], int):
        raise ValueError("max_items must be an integer")
    if not isinstance(config["purge_count"], int):
        raise ValueError("purge_count must be an integer")
    if not isinstance(config["next_level"], StoreABC):
        raise ValueError("next_level must be a StoreABC")
    if not issubclass(config["flavor"], CacheableObjABC):
        raise ValueError("flavor must be a subclass of GCABC")
    if config["max_items"] < 0:
        raise ValueError("max_items must be >= 0")
    if config["purge_count"] < 0:
        raise ValueError("purge_count must be >= 0")
    if config["max_items"] < config["purge_count"]:
        raise ValueError("purge_count must be <= max_items")


class CacheABC(StoreIllegal, StoreABC):
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
        self.flavor: type[CacheableObjABC] = config["flavor"]
        raise NotImplementedError("CacheABC.__init__ must be overridden")

    @abstractmethod
    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the cache.
        
        With the exception of the built-in 'fast' caches, all caches must
        check the next level for the item if it is not in the cache and pull it in
        as needed. The cache must also update the access sequence number by calling
        the touch method. This ensures the cache can purge the least recently used.
        """
        raise NotImplementedError("__getitem__ must be overridden")

    @abstractmethod
    def __setitem__(self, key: Hashable, value: CacheableObjABC) -> None:  # type: ignore
        """Set an item in the cache."""
        raise NotImplementedError("__setitem__ must be overridden")

    @abstractmethod
    def copyback(self) -> None:
        """Copy the cache back to the next level.
        Copy all dirty items back to the next level store. No purge or flush
        is done and the state of the cache and all access sequence numbers are
        left unchanged.
        """
        raise NotImplementedError("copy_back must be overridden")

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

    @abstractmethod
    def setdefault(self, key: Hashable, default: CacheableObjABC) -> Any:  # type: ignore pylint: disable=signature-differs
        """Set the default value for a key."""
        raise NotImplementedError("setdefault must be overridden")
