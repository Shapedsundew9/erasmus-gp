"""Cache Base Abstract Base Class"""
from typing import Any, TypedDict, Type
from logging import Logger, NullHandler, getLogger, DEBUG
from abc import abstractmethod
from egppy.gc_types.gc_abc import GCABC
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_illegal import StoreIllegal


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


class CacheConfig(TypedDict):
    """Cache configuration."""
    max_items: int  # Maximum number of items in the cache. 0 = infinite
    purge_count: int  # Number of items to purge when the cache is full
    next_level: StoreABC  # The next level of caching or storage
    flavor: Type[GCABC]  # The type of item stored in the cache


def validate_cache_config(config: CacheConfig) -> None:
    """Validate the cache configuration."""
    if not isinstance(config["max_items"], int):
        raise ValueError("max_items must be an integer")
    if not isinstance(config["purge_count"], int):
        raise ValueError("purge_count must be an integer")
    if not isinstance(config["next_level"], StoreABC):
        raise ValueError("next_level must be a StoreABC")
    if not issubclass(config["flavor"], GCABC):
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
        """Initialize the cache configuration.
        The members below are available to be set in derived classes.        
        """
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        self.flavor: Type[GCABC] = config["flavor"]
        assert False, "CacheABC.__init__ must be overridden"

    @abstractmethod
    def __getitem__(self, key: Any) -> GCABC:
        """Get an item from the cache."""
        assert False, "__getitem__ must be overridden"

    @abstractmethod
    def __setitem__(self, key: Any, value: GCABC) -> None:
        """Set an item in the cache."""
        assert False, "__setitem__ must be overridden"

    @abstractmethod
    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        assert False, "copy_back must be overridden"

    @abstractmethod
    def flush(self) -> None:
        """Flush the cache."""
        assert False, "flush must be overridden"

    @abstractmethod
    def purge(self, num: int) -> None:
        """Purge the cache of num items."""
        assert False, "purge must be overridden"

    @abstractmethod
    def touch(self, key: Any) -> None:
        """Touch the cache item to update the access sequence number."""
        assert False, "touch must be overridden"
