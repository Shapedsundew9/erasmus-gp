"""ObjectSet class.

A object set is a set of objects. It is a set of unique objects that may be referenced
in many places. The intent is to reduce memory consumption when a lot of duplicate
objects are used in a program.

>>> a = (2, 4, 5)
>>> b = (2, 4, 5)
>>> id(a)
128822992399424
>>> id(b)
128822991659840

"""

from collections.abc import Collection
from typing import Any, Iterator

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.common_obj_mixin import CommonObjMixin
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ObjectSet(Collection, CommonObjMixin, CommonObjABC):
    """ObjectSet class.

    A object set is a set of hashable objects. It is a set of unique objects that may be referenced
    in many places. The intent is to reduce memory consumption when a lot of duplicate
    objects are used in a program."""

    def __init__(self, name) -> None:
        """Initialize a ObjectSet object."""
        self._objects: dict = {}
        self._dupes = 0
        self.name = name

    def __contains__(self, tup) -> bool:
        """Check if a object is in the set."""
        return tup in self._objects

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over the objects in the set."""
        return iter(self._objects)

    def __len__(self) -> int:
        """Return the number of objects in the set."""
        return len(self._objects)

    def add(self, tup: Any) -> Any:
        """Add a object to the set."""
        # If the object is already in the set, return the existing object.
        added = self._objects.setdefault(tup, tup)
        self._dupes += added is not tup
        return added

    def remove(self, tup: Any) -> None:
        """Remove a object from the set."""
        del self._objects[tup]

    def verify(self) -> None:
        """Verify the ObjectSet object."""
        _logger.info(
            "Object Set '%s' has %d objects and %d duplicate add attempts.",
            self.name,
            len(self),
            self._dupes,
        )
        return super().verify()
