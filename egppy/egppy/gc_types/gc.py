"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from typing import Any, Iterator

from egpcommon.common import NULL_SHA256, sha256_signature
from egpcommon.conversions import decode_properties
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.end_point_type import ept_to_str
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


# Transient or runtime support GC key:values that do not go into store
EXCLUDED_KEYS: frozenset[str] = frozenset(["executable", "num_lines"])


def NULL_EXECUTABLE(_: tuple) -> tuple:  # pylint: disable=invalid-name
    """The Null Exectuable. Should never be executed."""
    raise RuntimeError("NULL_EXECUTABLE should never be executed.")


class GCABC(CacheableObjABC):
    """Genetic Code Abstract Base Class.

    Add Genetic Code classes have a very simple dictionary like interface for getting and
    setting members. All GC keys are strings from a frozen set of keys.
    """

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
    def setdefault(self, key: str, default: Any = None) -> Any:
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


class GCMixin:
    """Genetic Code Mixin Class."""

    def __eq__(self, other: object) -> bool:
        """Return True if the genetic code objects have the same signature."""
        if isinstance(other, GCABC):
            return self.signature() == other.signature()
        if isinstance(other, dict):
            other_signature = other.get("signature", NULL_SIGNATURE)
            if isinstance(other_signature, str) and len(other_signature) == 64:
                return self.signature().hex() == other_signature
        return False

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        for key in gcabc:
            self[key] = gcabc[key]

    def signature(self) -> bytes:
        """Return the signature of the genetic code object."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        if self["signature"] is NULL_SIGNATURE:
            self["signature"] = sha256_signature(
                self["gca"] if isinstance(self["gca"], bytes) else self["gca"].signature(),
                self["gcb"] if isinstance(self["gcb"], bytes) else self["gcb"].signature(),
                self["graph"].to_json(),
                self["meta_data"] if self["meta_data"] is not None else {},
            )
        return self["signature"]

    def to_json(self) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        retval = {}
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        for key in (included for included in self if included not in EXCLUDED_KEYS):
            value = self[key]
            if key == "properties":
                retval[key] = decode_properties(value)
            elif key == "meta_data":
                md = deepcopy(value)
                if (
                    "function" in md
                    and "python3" in md["function"]
                    and "0" in md["function"]["python3"]
                    and "imports" in md["function"]["python3"]["0"]
                ):
                    md["function"]["python3"]["0"]["imports"] = [
                        imp.to_json() for imp in md["function"]["python3"]["0"]["imports"]
                    ]
                retval[key] = md
            elif key.endswith("_types"):
                retval[key] = [ept_to_str(ept) for ept in value]
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value.signature().hex() if value is not NULL_GC else None
            elif getattr(self[key], "to_json", None) is not None:
                retval[key] = self[key].to_json()
            elif isinstance(value, bytes):
                retval[key] = value.hex() if value is not NULL_SIGNATURE else None
            elif isinstance(value, datetime):
                retval[key] = value.isoformat()
            else:
                retval[key] = value
                if _LOG_DEBUG:
                    assert isinstance(
                        value, (int, str, float, list, dict, tuple)
                    ), f"Invalid type: {type(value)}"
        return retval


class NullGC(CacheableDirtyDict, GCMixin, GCABC):
    """Genetic Code Protocol."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Initialize the genetic code object."""
        super().__init__(gcabc if gcabc is not None else {})
        super().__setitem__("num_lines", 0)  # No code lines in a NullGC
        super().__setitem__("executable", NULL_EXECUTABLE)

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
