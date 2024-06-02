"""A cache factory module to create cache objects."""
from typing import Any, Callable, Hashable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig, validate_cache_config
from egppy.storage.cache.cache_illegal import CacheIllegal
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.user_dict_cache_base import UserDictCacheBase
from egppy.storage.cache.dict_cache import DictCache
from egppy.gc_types.gc_abc import GCABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def cache_factory(cls: type[CacheABC]) -> type:
    """Create a cache object.

    Wraps the cls methods and adds derived methods to create a cache object.
    The cls must be a subclass of CacheBaseABC.

    Args:
        cls: The cache base class to wrap.

    Returns:
        A cache object.
    """
    if not issubclass(cls, CacheABC):
        raise ValueError("cls must be a subclass of CacheABC")

    def __init__(self, config: CacheConfig) -> None:
        """Constructor for Cache. Make sure config is valid and call base class constructor."""
        validate_cache_config(config=config)
        self.super = super(type(self), self)
        self.super.__init__(config=config)  # type: ignore

    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the cache."""
        if key not in self:
            # Need to ask the next level for the item. First check if we have space.
            self.purge_check()
            # The next level GC type must be flavored (cast) to the type stored here.
            self.super.__setitem__(key, self.flavor(self.next_level[key]))
        item: GCABC = self.super.__getitem__(key)
        self.touch(key=key)
        return item

    def __setitem__(self, key: Any, value: CacheableObjABC) -> None:
        """Set an item in the cache. If the cache is full make space first."""
        if key not in self:
            self.purge_check()
        self.super.__setitem__(key, self.flavor(value))
        self.touch(key=key)

    def purge_check(self) -> None:
        """Check if the cache needs to be purged."""
        length: int = len(self)
        if length >= self.max_items:
            assert length == self.max_items, (f"Cache length ({length}) is greater"
                f" than max_items ({self.max_items})")
            self.purge(num=self.purge_count)

    cls_name: str = cls.__name__.replace("Base", "")
    cls_methods: dict[str, Callable] = {
        '__init__': __init__,
        '__getitem__': __getitem__,
        '__setitem__': __setitem__,
        'purge_check': purge_check
    }
    return type(cls_name, (CacheIllegal, cls), cls_methods)


UserDictCache: type[UserDictCacheBase] = cache_factory(cls=UserDictCacheBase)
FastCache: type[DictCache] = type("FastCache", (CacheIllegal, DictCache), {})