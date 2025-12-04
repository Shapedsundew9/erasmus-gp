"""A python dictionary based cache."""

from collections.abc import Hashable, Iterator
from typing import Any, Callable

from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cache_base import CacheBase
from egppy.storage.cache.cache_mixin import CacheMixin
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Function to select sequence numbers for sorting
_KEY: Callable[[tuple[Any, int]], int] = lambda x: x[1]


class DictCache(CacheBase, CacheMixin, CacheABC):
    """Dictionary based cache. The cache functions wrap the builtin dict methods.
    Providing all the automated function of a cache with a small overhead.
    """

    def __init__(self, config: CacheConfig) -> None:
        """Initialize the cache."""
        super().__init__(config=config)
        self.data: dict[Hashable, CacheableObjABC] = {}

    def __contains__(self, key: Hashable) -> bool:
        """Check if the cache contains a key."""
        return key in self.data

    def __delitem__(self, key: Hashable) -> None:
        """Delete an item from the cache."""
        value: CacheableObjABC = self.data[key]
        if value.is_dirty():
            self.next_level[key] = value
        del self.data[key]

    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the cache."""
        if key not in self:
            # Need to ask the next level for the item. First check if we have space.
            self.purge_check()
            # The next level object type must be flavored (cast) to the type stored here.
            value = self.next_level[key]
            self.data[key] = self.flavor(value) if self._convert else value  # type: ignore
        item: CacheableObjABC = self.data[key]
        item.touch()
        return item

    def __iter__(self) -> Iterator:
        """Return an iterator over the cache."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return the number of items in the cache."""
        return len(self.data)

    def __setitem__(self, key: Any, value: CacheableObjABC) -> None:
        """Set an item in the cache. If the cache is full make space first."""
        if key not in self:
            self.purge_check()
        # The value must be flavored (cast) to the type stored here. At a minimum this is a shallow
        # copy so the next layer dirty flag is not affected.
        item = self.flavor(value)
        self.data[key] = item  # type: ignore
        item.dirty()  # type: ignore

    def purge(self, num: int) -> None:
        """Purge the cache of count items."""
        if num >= len(self):
            self.flush()
            return
        victims: list[tuple[Any, int]] = sorted(
            ((k, v.seq_num()) for k, v in self.data.items()), key=_KEY
        )[: self.purge_count]
        for key, _ in victims:
            del self[key]
