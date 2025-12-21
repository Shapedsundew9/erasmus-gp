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


# Deduplicator register
# This is a global registry of all deduplicators for monitoring purposes.
deduplicators_registry: dict[str, "ObjectDeduplicator"] = {}


def deduplicators_info() -> str:
    """Get information about all deduplicators."""
    return "\n".join(deduplicator.info() for deduplicator in deduplicators_registry.values())


def format_deduplicator_info(
    name: str, target_rate: float, hits: int, misses: int, currsize: int, maxsize: int | None
) -> str:
    """Format deduplicator cache information string."""
    rate = hits / (hits + misses) if (hits + misses) > 0 else 0.0
    occupancy = currsize / maxsize if maxsize is not None and maxsize > 0 else 0.0
    return (
        f"{name} Cache hits: {hits}\n"
        f"{name} Cache misses: {misses}\n"
        f"{name} Cache hit rate: {rate:.2%}"
        f" (target rate: {target_rate:.2%})\n"
        f"{name} Cache max size: {maxsize}\n"
        f"{name} Current cache size: {currsize} ({occupancy:.2%})\n"
    )


class ObjectDeduplicator(CommonObj):
    """ObjectDeduplicator class.

    There is no __setitem__ method. This is because addition to the dictionary must not overwrite
    existing objects. The __setitem__ method would overwrite the existing object with the new
    object. This is not the desired behavior. The add method must be used to add objects to the
    dictionary returning the existing object if it already exists.
    """

    __slots__ = ("_objects", "name", "target_rate")

    def __init__(self, name: str, size: int = 2**12, target_rate: float = 0.811) -> None:
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
        # Register & initialize the deduplicator if this is not a duplicate
        if name not in deduplicators_registry:
            deduplicators_registry[name] = self

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

    def __new__(cls, *args, **kwargs):
        """Prevent duplicate deduplicators with the same name."""
        name = args[0] if args else kwargs.get("name")
        if name in deduplicators_registry:
            return deduplicators_registry[name]
        return super().__new__(cls)

    def clear(self) -> None:
        """Clear the deduplicator cache."""
        self._objects.cache_clear()

    def info(self) -> str:
        """Print cache hit and miss statistics."""
        info = self._objects.cache_info()
        info_str = format_deduplicator_info(
            self.name,
            self.target_rate,
            info.hits,
            info.misses,
            info.currsize,
            info.maxsize,
        )
        _logger.info(info_str)
        return info_str


class IntDeduplicator(ObjectDeduplicator):
    """IntDeduplicator class for deduplicating immutable integer objects."""

    __slots__ = ("lmin", "lmax")

    def __init__(
        self,
        name: str,
        size: int = 2**12,
        target_rate: float = 0.811,
        lmin: int = 0,
        lmax: int = 2**12 - 1,
    ) -> None:
        """Initialize a IntDeduplicator object.

        Args:
            name: Name of the integer deduplicator.
            size: Size of the LRU cache.
            target_rate: Break even cache hit rate (information purposes only).
            lmin: Minimum integer value to deduplicate (inclusive).
            lmax: Maximum integer value to deduplicate (inclusive).
        """
        super().__init__(name, size, target_rate)
        self.lmin = lmin
        self.lmax = lmax

    def __getitem__(self, value: int) -> int:  # type: ignore
        """Get a deduplicated integer from the dict."""
        if self.lmin <= value <= self.lmax:
            return super().__getitem__(value)
        return value
