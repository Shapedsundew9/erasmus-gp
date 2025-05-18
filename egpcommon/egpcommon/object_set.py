"""ObjectSet class.

A object set is a set of objects. It is a set of unique objects that may be referenced
in many places. The intent is to reduce memory consumption when a lot of duplicate
objects are used in a program.
"""

from collections.abc import Collection
from typing import Any, Iterator
from weakref import WeakValueDictionary

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ObjectSet(Collection, CommonObj):
    """ObjectSet class.

    A object set is a set of hashable objects. It is a set of unique objects that may be referenced
    in many places. The intent is to reduce memory consumption when a lot of duplicate
    objects are used in a program."""

    def __init__(self, name) -> None:
        """Initialize a ObjectSet object."""
        self._objects: WeakValueDictionary = WeakValueDictionary()
        self._dupes = 0
        self._added = 0
        self.name = name

    def __contains__(self, obj) -> bool:
        """Check if a object is in the set."""
        return obj in self._objects

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over the objects in the set."""
        return iter(self._objects)

    def __len__(self) -> int:
        """Return the number of objects in the set."""
        return len(self._objects)

    def add(self, obj: Any) -> Any:
        """Add a object to the set."""
        # If the object is already in the set, return the existing object.
        added = self._objects.setdefault(obj, obj)
        assert (
            added.is_frozen() if isinstance(added, FreezableObject) else True
        ), "FreezableObjects must be frozen to be placed in an ObjectSet."
        self._dupes += added is not obj
        self._added += added is obj
        return added

    def clear(self) -> None:
        """Clear the set."""
        self._objects.clear()
        self._dupes = 0
        self._added = 0
        if _LOG_DEBUG:
            _logger.debug("Object Set '%s' cleared.", self.name)

    def info(self) -> str:
        """Print information about the object set."""
        info_str = (
            f"Object Set {self.name} has {len(self)} objects of "
            f"{self._added} added and {self._dupes} duplicate add attempts."
        )
        _logger.info(info_str)
        return info_str

    def remove(self, obj: Any) -> None:
        """Remove a object from the set."""
        del self._objects[obj]

    def verify(self) -> bool:
        """Verify the ObjectSet object."""
        self.info()
        return super().verify()
