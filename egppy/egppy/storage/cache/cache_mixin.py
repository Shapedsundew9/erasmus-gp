"""Cache Base class module."""

from collections.abc import Hashable

from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.cache.cache_abc import CacheABC
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.store.store_abc import StoreABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class CacheMixin:
    """Cache Base class has methods generic to all cache classes."""

    def consistency(self) -> None:
        """Check the cache for self consistency."""
        if not isinstance(self, CacheABC):
            raise RuntimeError("CacheMixin consistency called on non-CacheABC object.")
        _super = super()
        if not isinstance(_super, StoreABC):
            raise RuntimeError("CacheMixin method called on non-StoreABC object.")
        _super.consistency()

    def copyback(self) -> None:
        """Copy the cache back to the next level."""
        if not isinstance(self, CacheABC):
            raise RuntimeError("CacheMixin consistency called on non-CacheABC object.")
        for key, value in (x for x in self.items() if x[1].is_dirty()):
            self.next_level[key] = value
            value.clean()

    def copythrough(self) -> None:
        """Copy all dirty items back to the store."""
        if not isinstance(self, CacheABC):
            raise RuntimeError("CacheMixin consistency called on non-CacheABC object.")
        self.copyback()
        if isinstance(self.next_level, CacheABC):
            self.next_level.copythrough()

    def flush(self) -> None:
        """Flush the cache to the next level."""
        if not isinstance(self, CacheABC):
            raise RuntimeError("CacheMixin consistency called on non-CacheABC object.")
        self.copyback()
        self.clear()

    def purge(self, num: int) -> None:
        """Purge num items from the cache."""
        if not isinstance(self, CacheABC):
            raise RuntimeError("CacheMixin consistency called on non-CacheABC object.")
        if num >= len(self):
            self.flush()
            return
        for _ in range(num):
            key: Hashable
            value: CacheableObjABC
            key, value = self.popitem()
            if value.is_dirty():
                self.next_level[key] = value

    def purge_check(self) -> None:
        """Check if the cache needs to be purged."""
        assert isinstance(self, CacheABC), "CacheMixin consistency called on non-CacheABC object."
        length: int = len(self)
        if length >= self.max_items:
            if length != self.max_items:
                raise RuntimeError(
                    f"Cache length ({length}) is greater than max_items ({self.max_items})"
                )
            self.purge(num=self.purge_count)

    def verify(self) -> None:
        """Verify the cache.
        Every object stored in the cache is verified as well as basic
        cache parameters.
        """
        if not isinstance(self, CacheABC):
            raise ValueError("CacheMixin consistency called on non-CacheABC object.")
        for value in (v for v in self.values() if getattr(v, "verify", None) is not None):
            value.verify()

        if len(self) > self.max_items:
            raise ValueError("Cache size exceeds max_items.")
        _super = super()
        if not isinstance(_super, StoreABC):
            raise ValueError("CacheMixin method called on non-StoreABC object.")
        _super.verify()
