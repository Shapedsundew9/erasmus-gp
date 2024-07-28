"""Genetic Code Abstract Base Class."""
from __future__ import annotations
from typing import Any, Iterator, Protocol
from abc import abstractmethod
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# GC signatre None type management
# It is space efficient to have None types in the DB for signatures but not in the cache.
# In the GPC a None type is represented by a 0 SHA256
NULL_SIGNATURE_BYTES: bytes = b"\x00" * 32

# Evolve a pGC after this many 'uses'.
# MUST be a power of 2
M_CONSTANT: int = 1 << 4
M_MASK: int = M_CONSTANT - 1
NUM_PGC_LAYERS = 16
# With M_CONSTANT = 16 & NUM_PGC_LAYERS = 16 it will take 16**16 (== 2**64 == 18446744073709551616)
# population individual evolutions to require a 17th layer (and that is assuming all PGC's are
# children of the one in the 16th layer). Thats about 5.8 billion evolutions per second for
# 100 years. A million super fast cores doing 5.8 million per second...only an outside chance
# of hitting the limit if Erasmus becomes a global phenomenon and is not rewritten! Sensibly 
# future proofed.

# PROPERTIES must define the bit position of all the properties listed in
# the "properties" field of the entry_format.json definition.
PROPERTIES: dict[str, int] = {
    "extended": 1 << 0,
    "constant": 1 << 1,
    "conditional": 1 << 2,
    "deterministic": 1 << 3,
    "memory_modify": 1 << 4,
    "object_modify": 1 << 5,
    "physical": 1 << 6,
    "arithmetic": 1 << 16,
    "logical": 1 << 17,
    "bitwise": 1 << 18,
    "boolean": 1 << 19,
    "sequence": 1 << 20,
}


class GCABC(CacheableObjABC):
    """Genetic Code Abstract Base Class.
    
    Add Genetic Code classes have a very simple dictionary like interface for getting and
    setting members. All GC keys are strings from a frozen set of keys.
    """

    @abstractmethod
    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Initialize the genetic code object."""
        raise NotImplementedError("GCABC.__init__ must be overridden")

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        """Delete a key and value."""
        raise NotImplementedError("GCABC.__delitem__ must be overridden")

    @abstractmethod
    def __getitem__(self, key: str) -> Any:
        """Get the value of a key."""
        raise NotImplementedError("GCABC.__getitem__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Iterator:
        """Iterate over the keys."""
        raise NotImplementedError("GCABC.__iter__ must be overridden")

    @abstractmethod
    def __setitem__(self, key: str, value: Any) -> None:
        """Set the value of a key."""
        raise NotImplementedError("GCABC.__setitem__ must be overridden")

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of a key or return the default."""
        raise NotImplementedError("GCABC.get must be overridden")

    @abstractmethod
    def setdefault(self, key: str, default: Any) -> Any:
        """Set the value of a key if it does not exist and return the set value."""
        raise NotImplementedError("GCABC.setdefault must be overridden")

    @abstractmethod
    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        raise NotImplementedError("GCABC.set_members must be overridden")


class GCProtocol(Protocol):
    """Genetic Code Protocol."""

    GC_KEY_TYPES: dict[str, str]

    def __contains__(self, key: str) -> bool:
        """Delete a key and value."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __delitem__(self, key: str) -> None:
        """Delete a key and value."""

    def __getitem__(self, key: str) -> Any:
        """Get the value of a key."""

    def __iter__(self) -> Iterator:
        """Iterate over the keys."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the value of a key."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of a key or return the default."""
        ...  # pylint: disable=unnecessary-ellipsis

    def setdefault(self, key: str, default: Any) -> Any:
        """Set the value of a key if it does not exist and return the set value."""
        ...  # pylint: disable=unnecessary-ellipsis

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""


class GCMixin:
    """Genetic Code Mixin Class.
    
    This class should be inhereted low in the MRO so that more efficient standard access
    methods are used first.
    """

    def __iter__(self: GCProtocol) -> Iterator:
        """Iterate over the keys."""
        return iter(self.GC_KEY_TYPES)

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
