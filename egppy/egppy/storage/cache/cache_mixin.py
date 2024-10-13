"""Cache Base class module."""

from collections.abc import Hashable, ItemsView, ValuesView
from typing import Protocol

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.cache.cache_abc import CacheABC
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.store.store_abc import StoreABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheMixinProtocol(Protocol):
    """Supplies CacheABC method references to satisfy type checker.

    NOTE: This method is preferred over using ABC methods in the mixin
    class. This is because the mixin class will be used in multiple
    inheritance and MRO may attempt to call them (I think). This method
    avoids that issue.
    """

    @property
    def max_items(self) -> int:
        """Protocol placeholder for max_items property."""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def next_level(self) -> StoreABC:
        """Protocol placeholder for next_level property."""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def purge_count(self) -> int:
        """Protocol placeholder for purge_count property."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __len__(self) -> int:
        """Protocol placeholder for __len__ method."""
        ...  # pylint: disable=unnecessary-ellipsis

    def copyback(self) -> None:
        """Protocol placeholder for copyback method."""

    def copythrough(self) -> None:
        """Protocol placeholder for copythrough method."""

    def flush(self) -> None:
        """Protocol placeholder for flush method."""

    def items(self) -> ItemsView[Hashable, CacheableObjABC]:
        """Protocol placeholder for items method."""
        ...  # pylint: disable=unnecessary-ellipsis

    def popitem(self) -> tuple[Hashable, CacheableObjABC]:
        """Protocol placeholder for popitem method."""
        ...  # pylint: disable=unnecessary-ellipsis

    def purge(self, num: int) -> None:
        """Protocol placeholder for purge method."""

    def values(self) -> ValuesView:
        """Protocol placeholder for values method."""
        ...  #  pylint: disable=unnecessary-ellipsis


class CacheMixin:
    """Cache Base class has methods generic to all cache classes."""

    def consistency(self: CacheMixinProtocol) -> None:
        """Check the cache for self consistency."""
        for value in (v for v in self.values() if getattr(v, "consistency", None) is not None):
            value.consistency()
        super().consistency()

    def copyback(self: CacheMixinProtocol) -> None:
        """Copy the cache back to the next level."""
        for key, value in (x for x in self.items() if x[1].is_dirty()):
            self.next_level[key] = value
            value.clean()

    def copythrough(self: CacheMixinProtocol) -> None:
        """Copy all dirty items back to the store."""
        self.copyback()
        if isinstance(self.next_level, CacheABC):
            self.next_level.copythrough()

    def flush(self: CacheMixinProtocol) -> None:
        """Flush the cache to the next level."""
        self.copyback()
        super().clear()

    def purge(self: CacheMixinProtocol, num: int) -> None:
        """Purge num items from the cache."""
        if num >= len(self):
            self.flush()
            return
        for _ in range(num):
            key: Hashable
            value: CacheableObjABC
            key, value = self.popitem()
            if value.is_dirty():
                self.next_level[key] = value

    def purge_check(self: CacheMixinProtocol) -> None:
        """Check if the cache needs to be purged."""
        length: int = len(self)
        if length >= self.max_items:
            assert length == self.max_items, (
                f"Cache length ({length}) is greater" f" than max_items ({self.max_items})"
            )
            self.purge(num=self.purge_count)

    def verify(self: CacheMixinProtocol) -> None:
        """Verify the cache.
        Every object stored in the cache is verified as well as basic
        cache parameters.
        """
        for value in (v for v in self.values() if getattr(v, "verify", None) is not None):
            value.verify()

        assert len(self) <= self.max_items, "Cache size exceeds max_items."
        super().verify()
