"""Cache Base class module."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.cache.cache_abc import CacheConfig
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_base import StoreBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class CacheBase(StoreBase):
    """Cache Base class has methods generic to all cache classes."""

    def __init__(self, config: CacheConfig, level_one: bool = True) -> None:
        """Must be implemented by subclasses."""
        self.max_items: int = config["max_items"]
        self.purge_count: int = config["purge_count"]
        self.next_level: StoreABC = config["next_level"]
        super().__init__(config["flavor"])
        self.validate_cache_config(config)
        assert issubclass(self.flavor, CacheableObjABC)
        assert isinstance(self.next_level, StoreBase)
        self._convert = self.flavor != self.next_level.flavor
        self.level_one: bool = level_one

    def validate_cache_config(self, config: CacheConfig) -> None:
        """Validate the cache configuration."""
        if not isinstance(config["max_items"], int):
            raise ValueError("max_items must be an integer")
        if not isinstance(config["purge_count"], int):
            raise ValueError("purge_count must be an integer")
        if not isinstance(config["next_level"], StoreABC):
            raise ValueError("next_level must be a StoreABC")
        if not issubclass(config["flavor"], CacheableObjABC):
            raise ValueError("flavor must be a subclass of CacheableObjABC")
        if config["max_items"] < 0:
            raise ValueError("max_items must be >= 0")
        if config["purge_count"] < 0:
            raise ValueError("purge_count must be >= 0")
        if config["max_items"] < config["purge_count"]:
            raise ValueError("purge_count must be <= max_items")
