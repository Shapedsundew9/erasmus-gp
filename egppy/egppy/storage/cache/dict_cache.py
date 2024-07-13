"""A python dictionary based cache."""
from typing import Any, Callable
from collections.abc import Hashable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cache_mixin import CacheMixin
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cache_base import CacheBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class DictCache(dict[Hashable, CacheableObjABC], CacheBase, CacheMixin, CacheABC):
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
