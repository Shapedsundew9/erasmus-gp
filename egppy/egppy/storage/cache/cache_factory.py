"""A cache factory module to create cache objects."""
from typing import Any, Type
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig, validate_cache_config
from egppy.storage.cache.cache_illegal import CacheIllegal
from egppy.types.gc_abc import GCABC


def cache_factory(cls: Type[CacheABC], config: CacheConfig) -> CacheABC:
    """Create a cache object.

    Wraps the cls methods and adds derived methods to create a cache object.
    The cls must be a subclass of CacheBaseABC.

    Args:
        cls: The cache base class to wrap.

    Returns:
        A cache object.
    """
    validate_cache_config(config=config)
    if not issubclass(cls, CacheABC):
        raise ValueError("cls must be a subclass of CacheABC")

    if not config["max_items"]:
        # A fast cache has no size limits or access tracking.
        return type("FastCache", (CacheIllegal, cls), {})(config=config)

    class Cache(CacheIllegal, cls):
        """Cache store."""

        def __getitem__(self, key: Any) -> GCABC:
            """Get an item from the cache."""
            item: GCABC = super().__getitem__(key=key)
            self.touch(key=key)
            return item

        def __setitem__(self, key: Any, value: GCABC) -> None:
            """Set an item in the cache. If the cache is full make space first."""
            length: int = len(self)
            if length >= self.max_items and key not in self:
                assert length == self.max_items, (f"Cache length ({length}) is greater"
                    f" than max_items ({self.max_items})")
                self.purge(num=self.purge_count)
            super().__setitem__(key=key, value=value)  # type: ignore

    return Cache(config=config)
