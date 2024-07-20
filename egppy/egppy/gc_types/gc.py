"""Genetic Code Abstract Base Class."""
from __future__ import annotations
from typing import Any, Protocol
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict


class GCABC(CacheableObjABC):
    """Genetic Code Abstract Base Class.
    
    Add Genetic Code classes have a very simple dictionary like interface for getting and
    setting members. All GC keys are strings from a frozen set of keys.
    """

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Initialize the genetic code object."""
        raise NotImplementedError("GCABC.__init__ must be overridden")

    def __delitem__(self, key: str) -> None:
        """Delete a key and value."""
        raise NotImplementedError("GCABC.__delitem__ must be overridden")

    def __getitem__(self, key: str) -> Any:
        """Get the value of a key."""
        raise NotImplementedError("GCABC.__getitem__ must be overridden")

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the value of a key."""
        raise NotImplementedError("GCABC.__setitem__ must be overridden")

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of a key or return the default."""
        raise NotImplementedError("GCABC.get must be overridden")

    def setdefault(self, key: str, default: Any) -> Any:
        """Set the value of a key if it does not exist and return the set value."""
        raise NotImplementedError("GCABC.setdefault must be overridden")

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        raise NotImplementedError("GCABC.set_members must be overridden")


class GCProtocol(Protocol):
    """Genetic Code Protocol."""

    def __contains__(self, key: str) -> bool:
        """Delete a key and value."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __delitem__(self, key: str) -> None:
        """Delete a key and value."""

    def __getitem__(self, key: str) -> Any:
        """Get the value of a key."""

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the value of a key."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of a key or return the default."""

    def setdefault(self, key: str, default: Any) -> Any:
        """Set the value of a key if it does not exist and return the set value."""

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""


class GCMixin:
    """Genetic Code Mixin Class.
    
    This class should be inhereted low in the MRO so that more efficient standard access
    methods are used first.
    """
    GC_KEYS = frozenset({
        'graph',
        'gca',
        'gcb',
        'ancestora',
        'ancestorb',
        'pgc',
    })

    def get(self: GCProtocol, key: str, default: Any = None) -> Any:
        """Get the value of a key or return the default."""
        if key in self:
            return self[key]
        return default

    def setdefault(self: GCProtocol, key: str, default: Any) -> Any:
        """Set the value of a key if it does not exist and return the set value."""
        if key in self:
            return self[key]
        self[key] = default
        return default

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        for key in gcabc:
            self[key] = gcabc[key]


class NullGC(CacheableDirtyDict, GCMixin, GCABC):
    """Genetic Code Protocol."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Initialize the genetic code object."""
        super().__init__(gcabc)

    def __delitem__(self, key: str) -> None:
        """Cannot modifiy a NullGC."""
        raise RuntimeError("Cannot modify a NullGC")

    def __setitem__(self, key: str, value: Any) -> None:
        """Cannot modifiy a NullGC."""
        raise RuntimeError("Cannot modify a NullGC")

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        raise RuntimeError("Cannot modify a NullGC")


# The NullGC is a singleton object that is used to represent a NULL genetic code object.
NULL_GC = NullGC({})
