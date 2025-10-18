"""ObjectDict class.

An object dict is a weak value dictionary of unique objects that
may be referenced in many places. The intent is to reduce memory consumption when a
lot of duplicate objects are used in a program that require access by a unique key.
"""

from collections.abc import Collection, Hashable
from typing import Any, Iterator
from weakref import WeakValueDictionary

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import DEBUG, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class ObjectDict(Collection, CommonObj):
    """ObjectDict class.

    There is no __setitem__ method. This is because addition to the dictionary must not overwrite
    existing objects. The __setitem__ method would overwrite the existing object with the new
    object. This is not the desired behavior. The add method must be used to add objects to the
    dictionary returning the existing object if it already exists.
    """

    def __init__(self, name: str) -> None:
        """Initialize a ObjectDict object."""
        self._objects: WeakValueDictionary = WeakValueDictionary()
        self._dupes: int = 0
        self._added: int = 0
        self.name: str = name
        # TODO: In MONITOR mode and below send stats to prometheus

    def __contains__(self, key) -> bool:
        """Check if a object is in the dict."""
        return key in self._objects

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over the objects in the dict."""
        return iter(self._objects)

    def __len__(self) -> int:
        """Return the number of objects in the dict."""
        return len(self._objects)

    def __getitem__(self, key: Any) -> Any:
        """Get a object from the dict."""
        return self._objects[key]

    def add(self, key: Hashable, obj: Any) -> Any:
        """Add a object to the dict."""
        # If the object is already in the dict, return the existing object.
        added = self._objects.setdefault(key, obj)
        assert (
            added.is_frozen() if hasattr(added, "is_frozen") else True
        ), "FreezableObjects must be frozen to be placed in an ObjectDict."
        self._dupes += added is not obj
        self._added += added is obj
        return added

    def clear(self) -> None:
        """Clear the dict."""
        self._objects.clear()
        self._dupes = 0
        self._added = 0
        _logger.log(DEBUG, "Object %s '%s' cleared.", self.__class__, self.name)

    def info(self) -> str:
        """Print information about the object dict."""
        info_str = (
            f"Object {self.__class__} '{self.name}' has {len(self)} objects of "
            f"{self._added} added and {self._dupes} duplicate add attempts."
        )
        _logger.info(info_str)
        return info_str

    def remove(self, key: Hashable) -> None:
        """Remove a object from the dict."""
        del self._objects[key]

    def verify(self) -> bool:
        """Verify the ObjectDict object."""
        self.info()
        return super().verify()
