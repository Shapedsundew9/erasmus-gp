"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from itertools import count
from typing import Any, Iterator
from uuid import UUID

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.properties import GCType, PropertiesBD
from egppy.genetic_code.c_graph import CGraphType, c_graph_type
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import Row, SrcRow
from egppy.genetic_code.types_def import types_def_store
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)



# GC signature None type management
# NULL signatures are represented as None in both the cache and the DB.
# This reduces storage overhead and simplifies comparison operations.
NULL_SIGNATURE: None = None
NULL_PROBLEM: None = None
NULL_PROBLEM_SET: None = None


# Mermaid Chart header and footer
MERMAID_BLUE = "blue"
MERMAID_GREEN = "green"
MERMAID_RED = "red"
MERMAID_BLACK = "black"
MERMAID_HEADER: list[str] = ["flowchart TD"]
MERMAID_FOOTER: list[str] = [
    "classDef grey fill:#444444,stroke:#333333,stroke-width:2px",
    "classDef red fill:#A74747,stroke:#996666,stroke-width:2px",
    "classDef blue fill:#336699,stroke:#556688,stroke-width:2px",
    "classDef green fill:#576457,stroke:#667766,stroke-width:2px",
    "linkStyle default stroke:#AAAAAA,stroke-width:2px",
]


def mc_circle_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a circle."""
    return f'    {name}(("{label}")):::{color}'


def mc_connect_str(namea: str, nameb: str, connection: str = "-->") -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return f"    {namea} {connection} {nameb}"


def mc_hexagon_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a hexagon."""
    return f'    {name}{{{{"{label}"}}}}:::{color}'


def mc_rectangle_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a rectangle."""
    return f'    {name}("{label}"):::{color}'


# Mermaid Chart creation helper function
def mc_gc_str(gcabc: GCABC, prefix: str, row: Row, color: str = "") -> str:
    """Return a Mermaid Chart string representation of the GCABC node in the logical structure.
    By default a blue rectangle is used for a GC unless it is a codon which is a green circle.
    If a color is specified then that color rectangle is used.
    """
    if color == "":
        color = MERMAID_BLUE
        if gcabc.is_codon():
            if gcabc.is_meta():
                return mc_meta_str(gcabc, prefix, row)
            return mc_codon_str(gcabc, prefix, row)
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_rectangle_str(prefix + gcabc["signature"].hex()[-8:], label, color)


# Mermaid Chart creation helper function
def mc_unknown_str(gcabc: bytes, prefix: str, row: Row, color: str = MERMAID_RED) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc.hex()[-8:]}"
    return mc_circle_str(prefix + gcabc.hex()[-8:], label, color)


# Mermaid Chart creation helper function
def mc_codon_str(gcabc: GCABC, prefix: str, row: Row, color: str = MERMAID_GREEN) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_circle_str(prefix + gcabc["signature"].hex()[-8:], label, color)


# Mermaid Chart creation helper function
def mc_meta_str(gcabc: GCABC, prefix: str, row: Row, color: str = MERMAID_GREEN) -> str:
    """Return a Mermaid Chart string representation of the meta-codon structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_hexagon_str(prefix + gcabc["signature"].hex()[-8:], label, color)


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
        mc_rectangle_str("LogicalGC", "Logical GC", MERMAID_BLUE),
        mc_rectangle_str("ExecGC", "Executable GC", MERMAID_GREEN),
        mc_circle_str("Codon", "Codon", MERMAID_GREEN),
        mc_hexagon_str("MetaCodon", "Meta-Codon", MERMAID_GREEN),
        mc_circle_str("Unknown", "Unknown", MERMAID_RED),
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
    def is_pgc(self) -> bool:
        """Return True if the genetic code is a physical genetic code (PGC)."""
        raise NotImplementedError("GCABC.is_pgc must be overridden")

    @abstractmethod
    def is_conditional(self) -> bool:
        """Return True if the GCABC is conditional."""
        raise NotImplementedError("GCABC.is_conditional must be overridden")

    @abstractmethod
    def is_meta(self) -> bool:
        """Return True if the genetic code is a meta-codon."""
        raise NotImplementedError("GCABC.is_meta must be overridden")

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


class GCMixin(CommonObj):
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
        """Return True if the genetic code is a codon or meta-codon."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        codon = PropertiesBD.fast_fetch("gc_type", self["properties"])
        retval = codon == GCType.CODON or codon == GCType.META
        assert (
            retval and c_graph_type(self["cgraph"]) == CGraphType.PRIMITIVE
        ) or not retval, "If gc_type is a codon or meta-codon then cgraph must be primitive."
        assert (
            retval and self["ancestora"] is None and self["ancestorb"] is None
        ) or not retval, "Codons must not have ancestors."
        return retval

    def is_conditional(self) -> bool:
        """Return True if the genetic code is conditional."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        cgt: CGraphType = c_graph_type(self["cgraph"])
        return cgt == CGraphType.IF_THEN or cgt == CGraphType.IF_THEN_ELSE

    def is_pgc(self) -> bool:
        """Return True if the genetic code is a physical genetic code (PGC)."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        is_pgc = PropertiesBD.fast_fetch("is_pgc", self["properties"])
        return is_pgc

    def is_meta(self) -> bool:
        """Return True if the genetic code is a meta-codon."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        meta = PropertiesBD.fast_fetch("gc_type", self["properties"]) == GCType.META
        assert (
            meta and c_graph_type(self["cgraph"]) == CGraphType.PRIMITIVE
        ) or not meta, "If gc_type is a meta-codon then cgraph must be primitive."
        assert (
            meta and self["ancestora"] is None and self["ancestorb"] is None
        ) or not meta, "Meta-codons must not have ancestors."
        return meta

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
                if isinstance(gcx, GCABC) and gcx is not None:
                    work_queue.append((gcx, gcx["gca"], gcx["gcb"], prefix))
                    chart_txt.append(mc_gc_str(gcx, prefix, row))
                    chart_txt.append(mc_connection_str(gc, cts, gcx, prefix))
                if isinstance(gcx, bytes) and gcx is not None:
                    chart_txt.append(mc_unknown_str(gcx, prefix, row))
                    chart_txt.append(mc_connection_str(gc, cts, gcx, prefix))
        return "\n".join(MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

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
                # Make types human readable.
                retval[key] = [types_def_store[t].name for t in value]
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value["signature"].hex() if value is not None else None
            elif isinstance(value, CGraphABC):
                # Need to set json_c_graph to True so that the endpoints are correctly serialized
                retval[key] = value.to_json(json_c_graph=True)
            elif getattr(self[key], "to_json", None) is not None:
                retval[key] = self[key].to_json()
            elif isinstance(value, bytes):
                retval[key] = value.hex()
            elif value is None:
                retval[key] = None
            elif isinstance(value, datetime):
                retval[key] = value.isoformat()
            elif isinstance(value, UUID):
                retval[key] = str(value)
            else:
                retval[key] = value
                if _logger.isEnabledFor(DEBUG):
                    assert isinstance(
                        value, (int, str, float, list, dict, tuple)
                    ), f"Invalid type: {type(value)}"
        return retval
