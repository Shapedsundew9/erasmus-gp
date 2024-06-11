"""Cache Base class module."""
from typing import ValuesView
from collections.abc import Hashable, Collection, MutableSequence
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cache_abc import CacheConfig, validate_cache_config
from egppy.storage.store.store_abc import StoreABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheBase():
    """Cache Base class has methods generic to all cache classes."""

    def __init__(self, config: CacheConfig) -> None:
        """Must be implemented by subclasses."""
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        self.flavor: type[CacheableObjABC] = config["flavor"]
        validate_cache_config(config)

    def __contains__(self, key: Hashable) -> bool:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def __getitem__(self, key: Hashable) -> CacheableObjABC:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def __setitem__(self, key: Hashable, value: CacheableObjABC) -> None:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def consistency(self) -> None:
        """Check the cache for self consistency."""
        for value in self.values():
            value.consistency()

    def update_value(self, key: Hashable, value: Collection) -> None:
        """Update a value in the store."""
        if key in self:
            item = self[key]
            if issubclass(type(value), (list, MutableSequence)):
                self[key] = self.flavor(value)
            else:
                item.update(value)
                self[key] = item
        else:
            self[key] = self.flavor(value)

    def values(self) -> ValuesView[CacheableObjABC]:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def verify(self) -> None:
        """Verify the cache.
        Every object stored in the cache is verified as well as basic
        cache parameters.
        """
        for value in self.values():
            value.verify()

        assert len(self) <= self.max_items, "Cache size exceeds max_items."
