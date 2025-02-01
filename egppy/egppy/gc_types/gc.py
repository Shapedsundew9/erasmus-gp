"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from itertools import count
from typing import Any, Iterator

from egpcommon.common import NULL_SHA256, sha256_signature
from egpcommon.conversions import decode_properties
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.end_point_type import ept_to_str
from egppy.gc_graph.interface import interface
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


# For GC's with no executable (yet)
def NULL_EXECUTABLE(_: tuple) -> tuple:  # pylint: disable=invalid-name
    """The Null Exectuable. Should never be executed."""
    raise RuntimeError("NULL_EXECUTABLE should never be executed.")


# Mermaid Chart header and footer
MERMAID_GC_COLOR = "blue"
MERMAID_CODON_COLOR = "green"
MERMAID_UNKNOWN_COLOR = "red"
MERMAID_HEADER: list[str] = ["flowchart TD"]
MERMAID_FOOTER: list[str] = [
    "classDef grey fill:#444444,stroke:#333333,stroke-width:2px",
    "classDef red fill:#A74747,stroke:#996666,stroke-width:2px",
    "classDef blue fill:#336699,stroke:#556688,stroke-width:2px",
    "classDef green fill:#576457,stroke:#667766,stroke-width:2px",
    "linkStyle default stroke:#AAAAAA,stroke-width:2px",
]


def mc_rectangle_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a rectangle."""
    return f"    {name}({label}):::{color}"


def mc_connect_str(namea: str, nameb: str, connection: str = "-->") -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return f"    {namea} {connection} {nameb}"


def mc_circle_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a circle."""
    return f"    {name}(({label})):::{color}"


# Mermaid Chart creation helper function
def mc_gc_str(gcabc: GCABC, prefix: str, color: str = "") -> str:
    """Return a Mermaid Chart string representation of the GCABC node in the logical structure.
    By default a blue rectangle is used for a GC unless it is a codon which is a green circle.
    If a color is specified then that color rectangle is used.
    """
    if color == "":
        color = MERMAID_GC_COLOR
        if gcabc["num_codons"] == 1:
            return mc_codon_str(gcabc, prefix)
    return mc_rectangle_str(
        prefix + gcabc.signature().hex()[-8:], gcabc.signature().hex()[-8:], color
    )


# Mermaid Chart creation helper function
def mc_unknown_str(gcabc: bytes, prefix: str, color: str = MERMAID_UNKNOWN_COLOR) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCABC in the logical structure."""
    return mc_circle_str(prefix + gcabc.hex()[-8:], gcabc.hex()[-8:], color)


# Mermaid Chart creation helper function
def mc_codon_str(gcabc: GCABC, prefix: str, color: str = MERMAID_CODON_COLOR) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCABC in the logical structure."""
    return mc_circle_str(prefix + gcabc.signature().hex()[-8:], gcabc.signature().hex()[-8:], color)


# Mermaid Chart creation helper function
def mc_connection_str(gca: GCABC | bytes, prefixa: str, gcb: GCABC | bytes, prefixb: str) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    _gca: str = gca.signature().hex()[-8:] if isinstance(gca, GCABC) else gca.hex()[-8:]
    _gcb: str = gcb.signature().hex()[-8:] if isinstance(gcb, GCABC) else gcb.hex()[-8:]
    return mc_connect_str(prefixa + _gca, prefixb + _gcb)


# Mermaid Chart key to node shape and color mapping
_MERMAID_KEY: list[str] = (
    [
        "```mermaid\n",
        "flowchart TD\n",
        mc_rectangle_str("GC", "Non-codon GC", MERMAID_GC_COLOR),
        mc_circle_str("Codon", "Codon GC", MERMAID_CODON_COLOR),
        mc_circle_str("Unknown", "Unknown", MERMAID_UNKNOWN_COLOR),
        '    text["Signature[-8:]"]\n',
    ]
    + MERMAID_FOOTER
    + ["```"]
)


def mermaid_key() -> str:
    """Return a Mermaid chart key."""
    return "\n".join(_MERMAID_KEY)


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
    def logical_mermaid_chart(self) -> str:
        """Return a Mermaid chart of the logical genetic code structure."""
        raise NotImplementedError("GCABC.logical_mermaid_chart must be overridden")

    @abstractmethod
    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set the value of a key if it does not exist and return the set value."""
        raise NotImplementedError("GCABC.setdefault must be overridden")

    @abstractmethod
    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        raise NotImplementedError("GCABC.set_members must be overridden")

    @abstractmethod
    def signature(self, field: str = "signature") -> bytes:
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

    def logical_mermaid_chart(self) -> str:
        """Return a Mermaid chart of the logical genetic code structure."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        work_queue: list[tuple[GCABC, GCABC | bytes, GCABC | bytes, str]] = [
            (self, self["gca"], self["gcb"], "0")
        ]
        chart_txt: list[str] = [mc_gc_str(self, "0")]
        # Each instance of the same GC must have a unique id in the chart
        counter = count(1)
        while work_queue:
            gc, gca, gcb, cts = work_queue.pop(0)
            # deepcode ignore unguarded~next~call: This is an infinite generator
            nct = str(next(counter))
            if isinstance(gca, GCABC) and gca is not NULL_GC:
                work_queue.append((gca, gca["gca"], gca["gcb"], "a" + nct))
                chart_txt.append(mc_gc_str(gca, "a" + nct))
                chart_txt.append(mc_connection_str(gc, cts, gca, "a" + nct))
            if isinstance(gca, bytes) and gca is not NULL_SIGNATURE:
                chart_txt.append(mc_unknown_str(gca, "a" + nct))
                chart_txt.append(mc_connection_str(gc, cts, gca, "a" + nct))
            if isinstance(gcb, GCABC) and gcb is not NULL_GC:
                work_queue.append((gcb, gcb["gca"], gcb["gcb"], "b" + nct))
                chart_txt.append(mc_gc_str(gcb, "b" + nct))
                chart_txt.append(mc_connection_str(gc, cts, gcb, "b" + nct))
            if isinstance(gcb, bytes) and gcb is not NULL_SIGNATURE:
                chart_txt.append(mc_unknown_str(gcb, "b" + nct))
                chart_txt.append(mc_connection_str(gc, cts, gcb, "b" + nct))
        return "\n".join(MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        for key in gcabc:
            self[key] = gcabc[key]

    def signature(self, field: str = "signature") -> bytes:
        """Return the signature of the genetic code field.

        Note that gc[field] can be either bytes or GCABC objects. bytes are used
        when the GC is not in the cache. GCABC objects are used when the GC is in the cache.
        This saves 97 bytes per field in the cache (a 32 byte bytes object = 97 bytes). With
        a GC having 6 fields this saves 582 bytes per GC. With 1,000,000 GCs this saves 582 MB.
        """
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        value: GCABC | bytes = self[field]
        if field == "signature":
            if value is NULL_SIGNATURE:
                gca: GCABC | bytes = self["gca"]
                gcb: GCABC | bytes = self["gcb"]

                # An optimisation is to avoid going through all the work stack logic
                # if gca and gcb have defined signatures in the immediate GCs.
                if (
                    gca is not NULL_GC
                    and isinstance(gca, GCABC)
                    and gca["signature"] is NULL_SIGNATURE
                ) or (
                    gcb is not NULL_GC
                    and isinstance(gcb, GCABC)
                    and gcb["signature"] is NULL_SIGNATURE
                ):
                    # To avoid the stack popping with deep recurision, as may happen if we get
                    # succesive steady state exceptions or evolve a very complex PGC, we build a
                    # work stack of GC's to calaculate the signatures of.
                    work_stack = [(gca, gcb)]
                    work_items = 0
                    while work_items < len(work_stack):
                        work_items = len(work_stack)
                        gca, gcb = work_stack[-1]
                        if (
                            gca is not NULL_GC
                            and isinstance(gca, GCABC)
                            and gca["signature"] is NULL_SIGNATURE
                        ):
                            work_stack.append((gca["gca"], gca["gcb"]))
                        if (
                            gcb is not NULL_GC
                            and isinstance(gcb, GCABC)
                            and gcb["signature"] is NULL_SIGNATURE
                        ):
                            work_stack.append((gcb["gca"], gcb["gcb"]))

                    # Once we have the stack we can iteratively calaculate signatures
                    # from the bottom up.
                    # NOTE: There will always be at least one iteration
                    for gca, gcb in reversed(work_stack):
                        assert isinstance(gca, GCABC), "GC must be a GCABC object."
                        assert isinstance(gcb, GCABC), "GC must be a GCABC object."
                        gca_sig: bytes = gca.signature()
                        gcb_sig: bytes = gcb.signature()
                else:
                    gca_sig = gca.signature() if isinstance(gca, GCABC) else gca
                    gcb_sig = gcb.signature() if isinstance(gcb, GCABC) else gcb

                self["signature"] = sha256_signature(
                    gca_sig,  # type: ignore Guaranteed to be a bytes objects
                    gcb_sig,  # type: ignore Guaranteed to be a bytes objects
                    self["graph"].to_json(),
                    self["meta_data"] if self["meta_data"] is not None else {},
                )
            return self["signature"]
        elif field.startswith("problem"):
            assert isinstance(value, bytes), "Problem signatures must be bytes."
            return value
        else:
            # The assert below addresses a peculiarity of pylance to insist something declared
            # as bytes is not bytes. Is this a bug in pylance?
            assert not isinstance(
                value, (bytearray, memoryview)
            ), "Invalid type for signature field."
            return value if isinstance(value, bytes) else value.signature()

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
                retval[key] = [ept_to_str(ept) for ept in interface(value)]
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

    def signature(self, field: str = "signature") -> bytes:
        """Return the signature of the genetic code object."""
        return NULL_SIGNATURE


# The NullGC is a singleton object that is used to represent a NULL genetic code object.
NULL_GC = NullGC({})
