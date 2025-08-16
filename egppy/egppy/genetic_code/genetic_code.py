"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from itertools import count
from typing import Any, Callable, Iterator
from uuid import UUID

from egpcommon.common import NULL_SHA256
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.properties import PropertiesBD
from egppy.genetic_code.c_graph import CGraph, CGraphType, c_graph_type
from egppy.genetic_code.c_graph_constants import Row, SrcRow
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# GC signature None type management
# It is space efficient to have None types in the DB for signatures but not in the cache.
# In the GPC a None type is represented by a 0 SHA256
NULL_SIGNATURE: bytes = NULL_SHA256
NULL_PROBLEM: bytes = NULL_SHA256
NULL_PROBLEM_SET: bytes = NULL_SHA256


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
    return f'    {name}("{label}"):::{color}'


def mc_connect_str(namea: str, nameb: str, connection: str = "-->") -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return f"    {namea} {connection} {nameb}"


def mc_circle_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a circle."""
    return f'    {name}(("{label}")):::{color}'


# Mermaid Chart creation helper function
def mc_gc_str(gcabc: GCABC, prefix: str, row: Row, color: str = "") -> str:
    """Return a Mermaid Chart string representation of the GCABC node in the logical structure.
    By default a blue rectangle is used for a GC unless it is a codon which is a green circle.
    If a color is specified then that color rectangle is used.
    """
    if color == "":
        color = MERMAID_GC_COLOR
        if gcabc["num_codons"] == 1:
            return mc_codon_str(gcabc, prefix, row)
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_rectangle_str(prefix + gcabc["signature"].hex()[-8:], label, color)


# Mermaid Chart creation helper function
def mc_unknown_str(gcabc: bytes, prefix: str, row: Row, color: str = MERMAID_UNKNOWN_COLOR) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc.hex()[-8:]}"
    return mc_circle_str(prefix + gcabc.hex()[-8:], label, color)


# Mermaid Chart creation helper function
def mc_codon_str(gcabc: GCABC, prefix: str, row: Row, color: str = MERMAID_CODON_COLOR) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_circle_str(prefix + gcabc["signature"].hex()[-8:], label, color)


# Mermaid Chart creation helper function
def mc_connection_str(gca: GCABC | bytes, prefixa: str, gcb: GCABC | bytes, prefixb: str) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    _gca: str = gca["signature"].hex()[-8:] if isinstance(gca, GCABC) else gca.hex()[-8:]
    _gcb: str = gcb["signature"].hex()[-8:] if isinstance(gcb, GCABC) else gcb.hex()[-8:]
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

    GC_KEY_TYPES: dict[str, dict[str, str | bool]]

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
    def is_codon(self) -> bool:
        """Return True if the GCABC is a codon."""
        raise NotImplementedError("GCABC.is_codon must be overridden")

    @abstractmethod
    def is_conditional(self) -> bool:
        """Return True if the GCABC is conditional."""
        raise NotImplementedError("GCABC.is_conditional must be overridden")

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


class GCMixin:
    """Genetic Code Mixin Class."""

    def __eq__(self, other: object) -> bool:
        """Return True if the genetic code objects have the same signature."""
        assert isinstance(self, GCABC)
        return isinstance(other, GCABC) and self["signature"] == other["signature"]

    def __hash__(self) -> int:
        """Return the hash of the genetic code object.
        Signature is guaranteed unique for a given genetic code.
        """
        assert isinstance(self, GCABC)
        assert self["signature"] is not NULL_SIGNATURE, "Signature must not be NULL."
        return hash(self["signature"])

    def is_codon(self) -> bool:
        """Return True if the genetic code is a codon."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        return c_graph_type(self["cgraph"]) == CGraphType.PRIMITIVE

    def is_conditional(self) -> bool:
        """Return True if the genetic code is conditional."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        cgt: CGraphType = c_graph_type(self["cgraph"])
        return cgt == CGraphType.IF_THEN or cgt == CGraphType.IF_THEN_ELSE

    def logical_mermaid_chart(self) -> str:
        """Return a Mermaid chart of the logical genetic code structure."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        work_queue: list[tuple[GCABC, GCABC | bytes, GCABC | bytes, str]] = [
            (self, self["gca"], self["gcb"], "0")
        ]
        chart_txt: list[str] = [mc_gc_str(self, "0", SrcRow.I)]
        # Each instance of the same GC must have a unique id in the chart
        counter = count(1)
        while work_queue:
            gc, gca, gcb, cts = work_queue.pop(0)
            # deepcode ignore unguarded~next~call: This is an infinite generator
            nct = str(next(counter))
            for gcx, prefix, row in [(gca, "a" + nct, SrcRow.A), (gcb, "b" + nct, SrcRow.B)]:
                if isinstance(gcx, GCABC) and gcx is not NULL_SIGNATURE:
                    work_queue.append((gcx, gcx["gca"], gcx["gcb"], prefix))
                    chart_txt.append(mc_gc_str(gcx, prefix, row))
                    chart_txt.append(mc_connection_str(gc, cts, gcx, prefix))
                if isinstance(gcx, bytes) and gcx is not NULL_SIGNATURE:
                    chart_txt.append(mc_unknown_str(gcx, prefix, row))
                    chart_txt.append(mc_connection_str(gc, cts, gcx, prefix))
        return "\n".join(MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

    def resolve_inherited_members(self, find_gc: Callable[[bytes], GCABC]) -> None:
        """Resolve inherited members from ancestor GCs."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        gca = self["gca"]
        gcb = self["gcb"]
        if gca is NULL_SIGNATURE:
            raise ValueError("Cannot resolve inherited members. GC is a codon.")
        gca = find_gc(gca)

        # Populate inherited members as if just GCA is set
        self["num_codons"] = gca["num_codons"]
        self["num_codes"] = gca["num_codes"] + 1
        self["generation"] = gca["generation"] + 1
        self["code_depth"] = gca["code_depth"] + 1

        # Ad in this GC must be the same as Is in the GCA
        # NOTE: That the TypesDef ObjectSet should ensure they are the same object
        if not all(a.typ is i.typ for a, i in zip(self["cgraph"]["Ad"], gca["cgraph"]["Is"])):
            raise ValueError("Input types do not match for GCA")

        # As in this GC must be the same as Od in the GCA
        if not all(a.typ is o.typ for a, o in zip(self["cgraph"]["As"], gca["cgraph"]["Od"])):
            raise ValueError("Output types do not match for GCA")

        # If GCB exists modify
        if gcb is not NULL_SIGNATURE:
            gcb = find_gc(gcb)
            self["num_codons"] += gcb["num_codons"]
            self["num_codes"] += gcb["num_codes"]
            self["generation"] = max(self["generation"], gcb["generation"] + 1)
            self["code_depth"] = max(self["code_depth"], gcb["code_depth"] + 1)

            # Bd in this GC must be the same as Is in the GCB
            # NOTE: That the TypesDef ObjectSet should ensure they are the same object
            if not all(b.typ is i.typ for b, i in zip(self["cgraph"]["Bd"], gcb["cgraph"]["Is"])):
                raise ValueError("Input types do not match for GCB")

            # Bs in this GC must be the same as Od in the GCB
            if not all(b.typ is o.typ for b, o in zip(self["cgraph"]["Bs"], gcb["cgraph"]["Od"])):
                raise ValueError("Output types do not match for GCB")

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        for key in gcabc:
            self[key] = gcabc[key]

    def to_json(self) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        retval = {}
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        # Only keys that are persisted in the DB are included in the JSON.
        for key in (k for k in self if self.GC_KEY_TYPES.get(k, {})):
            value = self[key]
            if key == "meta_data":
                assert isinstance(value, dict), "Meta data must be a dict."
                md = deepcopy(value)
                if (
                    "function" in md
                    and "python3" in md["function"]
                    and "0" in md["function"]["python3"]
                    and "imports" in md["function"]["python3"]["0"]
                ):
                    md["function"]["python3"]["0"]["imports"] = [
                        imp.to_json() for imp in self["imports"]
                    ]
                retval[key] = md
            elif key == "properties":
                # Make properties humman readable.
                assert isinstance(value, int), "Properties must be an int."
                retval[key] = PropertiesBD(value).to_json()
            elif key.endswith("_types"):
                # Make types humman readable.
                retval[key] = value
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value["signature"].hex() if value is not NULL_SIGNATURE else None
            elif isinstance(value, CGraph):
                # Need to set json_c_graph to True so that the end points are correctly serialized
                retval[key] = value.to_json(json_c_graph=True)
            elif getattr(self[key], "to_json", None) is not None:
                retval[key] = self[key].to_json()
            elif isinstance(value, bytes):
                retval[key] = value.hex() if value is not NULL_SIGNATURE else None
            elif isinstance(value, datetime):
                retval[key] = value.isoformat()
            elif isinstance(value, UUID):
                retval[key] = str(value)
            else:
                retval[key] = value
                if _LOG_DEBUG:
                    assert isinstance(
                        value, (int, str, float, list, dict, tuple)
                    ), f"Invalid type: {type(value)}"
        return retval
