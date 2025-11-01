"""ObjectDeduplicator class.

An object dict is a weak value dictionary of unique objects that
may be referenced in many places. The intent is to reduce memory consumption when a
lot of duplicate objects are used in a program that require access by a unique obj.
"""

from collections.abc import Hashable
from functools import lru_cache
from typing import Any

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class ObjectDeduplicator(CommonObj):
    """ObjectDeduplicator class.

    There is no __setitem__ method. This is because addition to the dictionary must not overwrite
    existing objects. The __setitem__ method would overwrite the existing object with the new
    object. This is not the desired behavior. The add method must be used to add objects to the
    dictionary returning the existing object if it already exists.
    """

    __slots__ = ("_objects", "name", "target_rate")

    def __init__(self, name: str, size: int = 2**16, target_rate: float = 0.811) -> None:
        """Initialize a ObjectDeduplicator object.

        Up to `size` unique objects will be deduplicated. If more unique objects are added
        the least recently used objects will be discarded which means they may be added again
        (and thus duplicated if the previous instance has not yet been garbage collected).

        The size should be chosen to be large enough to hold the most frequently created
        unique hash objects as these will be the 'least recently used'.

        See `egpcommon.docs.object_deduplicator.md` for more information.

        Args:
            name: Name of the object deduplicator.
            size: Size of the LRU cache.
            target_rate: Break even cache hit rate (information purposes only).
        """

        @lru_cache(maxsize=size)
        def cached_hash(obj: Hashable) -> Hashable:
            return obj

        self._objects = cached_hash
        self.name: str = name
        self.target_rate: float = target_rate
        # TODO: In MONITOR mode and below send stats to prometheus

    def __getitem__(self, obj: Hashable) -> Any:
        """Get a object from the dict."""
        assert obj.is_frozen() if hasattr(obj, "is_frozen") else True, (  # type: ignore
            "FreezableObjects must be frozen to be placed in an ObjectDeduplicator."
        )
        return self._objects(obj)

    def info(self) -> str:
        """Print cache hit and miss statistics."""
        info = self._objects.cache_info()
        rate = info.hits / (info.hits + info.misses) if (info.hits + info.misses) > 0 else 0.0
        info_str = (
            f"{self.name} Cache hits: {info.hits}\n"
            f"{self.name} Cache misses: {info.misses}\n"
            f"{self.name} Cache hit rate: {rate:.2%}"
            f" (target rate: {self.target_rate:.2%})"
            f" Cache max size: {info.maxsize}\n"
            f"{self.name} Current cache size: {info.currsize}"
        )
        _logger.info(info_str)
        return info_str
