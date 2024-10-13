"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from hashlib import sha256
from pprint import pformat
from typing import Any, Iterator, Protocol

from egpcommon.common import NULL_SHA256
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# GC signatre None type management
# It is space efficient to have None types in the DB for signatures but not in the cache.
# In the GPC a None type is represented by a 0 SHA256
NULL_SIGNATURE: bytes = NULL_SHA256
NULL_PROBLEM: bytes = NULL_SHA256
NULL_PROBLEM_SET: bytes = NULL_SHA256

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


def encode_properties(obj: dict[str, bool] | int | None) -> int:
    """Encode the properties dictionary into its integer representation.

    The properties field is a dictionary of properties to boolean values. Each
    property maps to a specific bit of a 64 bit value as defined
    by the _PROPERTIES dictionary.

    Args
    ----
    obj(dict): Properties dictionary.

    Returns
    -------
    (int): Integer representation of the properties dictionary.
    """
    if isinstance(obj, dict):
        bitfield: int = 0
        for k in (x[0] for x in obj.items() if x[1]):
            bitfield |= PROPERTIES[k]
        return bitfield
    if isinstance(obj, int):
        return obj
    if obj is None:
        return 0
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'dict' or integer type.")


def decode_properties(obj: int | dict[str, bool] | None) -> dict[str, bool]:
    """Decode the properties dictionary from its integer representation.

    The properties field is a dictionary of properties to boolean values. Each
    property maps to a specific bit of a 64 bit value as defined
    by the _PROPERTIES dictionary.

    Args
    ----
    obj(int): Integer representation of the properties dictionary.

    Returns
    -------
    (dict): Properties dictionary.
    """
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, int):
        return {b: bool(f & obj) for b, f in PROPERTIES.items()}
    if obj is None:
        return {b: False for b, f in PROPERTIES.items()}
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'dict' or integer type.")


class GCABC(CacheableObjABC):
    """Genetic Code Abstract Base Class.

    Add Genetic Code classes have a very simple dictionary like interface for getting and
    setting members. All GC keys are strings from a frozen set of keys.
    """

    @abstractmethod
    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
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

    @abstractmethod
    def signature(self) -> bytes:
        """Return the signature of the genetic code."""
        raise NotImplementedError("GCABC.signature must be overridden")


class GCProtocol(Protocol):
    """Genetic Code Protocol."""

    GC_KEY_TYPES: dict[str, str]
    REFERENCE_KEYS: set[str]

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

    def signature(self) -> bytes:
        """Return the signature of the genetic code."""
        ...  # pylint: disable=unnecessary-ellipsis


class GCMixin:
    """Genetic Code Mixin Class.

    This class should be inhereted low in the MRO so that more efficient standard access
    methods are used first.
    """

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        for key in gcabc:
            self[key] = gcabc[key]

    def signature(self: GCProtocol) -> bytes:
        """Return the signature of the genetic code object."""
        if self["signature"] is NULL_SIGNATURE:
            hash_obj = sha256(self["gca"].signature())
            hash_obj.update(self["gcb"].signature())
            hash_obj.update(pformat(self["graph"].to_json(), compact=True).encode())
            meta_data = self.get("meta_data", {})
            if "function" in meta_data:
                hash_obj.update(meta_data["function"]["python3"]["0"]["inline"].encode())
                if "code" in meta_data["function"]["python3"]["0"]:
                    hash_obj.update(meta_data["function"]["python3"]["0"]["code"].encode())
            self["signature"] = hash_obj.digest()
        return self["signature"]


class GCBase(GCProtocol):
    """Genetic Code Base Class."""

    def __eq__(self: GCProtocol, other: object) -> bool:
        """Return True if the genetic code objects have the same signature."""
        if isinstance(other, GCABC):
            return self.signature() == other.signature()
        if isinstance(other, dict):
            other_signature = other.get("signature", NULL_SIGNATURE)
            if isinstance(other_signature, str) and len(other_signature) == 64:
                return self.signature().hex() == other_signature
        return False

    def to_json(self: GCProtocol) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        retval = {}
        for key in self:
            value = self[key]
            if key == "properties":
                retval[key] = decode_properties(value)
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value.signature().hex()
            elif getattr(self[key], "to_json", None) is not None:
                retval[key] = self[key].to_json()
            elif isinstance(value, bytes):
                retval[key] = value.hex()
            elif isinstance(value, datetime):
                retval[key] = value.isoformat()
            else:
                retval[key] = value
                if _LOG_DEBUG:
                    assert isinstance(
                        value, (int, str, float, list, dict)
                    ), f"Invalid type: {type(value)}"
        return retval


class NullGC(CacheableDirtyDict, GCMixin, GCABC):
    """Genetic Code Protocol."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Initialize the genetic code object."""
        super().__init__(gcabc if gcabc is not None else {})

    def __delitem__(self, key: str) -> None:
        """Cannot modifiy a NullGC."""
        raise RuntimeError("Cannot modify a NullGC")

    def __setitem__(self, key: str, value: Any) -> None:
        """Cannot modifiy a NullGC."""
        raise RuntimeError("Cannot modify a NullGC")

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        raise RuntimeError("Cannot modify a NullGC")

    def signature(self) -> bytes:
        """Return the signature of the genetic code object."""
        return NULL_SIGNATURE


# The NullGC is a singleton object that is used to represent a NULL genetic code object.
NULL_GC = NullGC({})
