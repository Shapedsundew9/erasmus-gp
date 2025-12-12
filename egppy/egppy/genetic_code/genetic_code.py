"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Iterator

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import Row
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


# Mermaid Chart creation helper function
def mc_codon_str(gcabc: GCABC, prefix: str, row: Row, color: str = MERMAID_GREEN) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_circle_str(prefix + gcabc["signature"].hex()[-8:], label, color)


def mc_connect_str(namea: str, nameb: str, connection: str = "-->") -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return f"    {namea} {connection} {nameb}"


# Mermaid Chart creation helper function
def mc_connection_str(gca: GCABC | bytes, prefixa: str, gcb: GCABC | bytes, prefixb: str) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    _gca: str = gca["signature"].hex()[-8:] if isinstance(gca, GCABC) else gca.hex()[-8:]
    _gcb: str = gcb["signature"].hex()[-8:] if isinstance(gcb, GCABC) else gcb.hex()[-8:]
    return mc_connect_str(prefixa + _gca, prefixb + _gcb)


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


def mc_hexagon_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a hexagon."""
    return f'    {name}{{{{"{label}"}}}}:::{color}'


# Mermaid Chart creation helper function
def mc_meta_str(gcabc: GCABC, prefix: str, row: Row, color: str = MERMAID_GREEN) -> str:
    """Return a Mermaid Chart string representation of the meta-codon structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc['signature'].hex()[-8:]}"
    return mc_hexagon_str(prefix + gcabc["signature"].hex()[-8:], label, color)


def mc_rectangle_str(name: str, label: str, color: str) -> str:
    """Return a Mermaid Chart string representation of a rectangle."""
    return f'    {name}("{label}"):::{color}'


# Mermaid Chart creation helper function
def mc_unknown_str(gcabc: bytes, prefix: str, row: Row, color: str = MERMAID_RED) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCABC in the logical structure."""
    label = f"{row}<br>{gcabc.hex()[-8:]}"
    return mc_circle_str(prefix + gcabc.hex()[-8:], label, color)


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
    def __len__(self) -> int:
        """Return the number of keys."""
        raise NotImplementedError("GCABC.__len__ must be overridden")

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
    def is_meta(self) -> bool:
        """Return True if the genetic code is a meta-codon."""
        raise NotImplementedError("GCABC.is_meta must be overridden")

    @abstractmethod
    def is_pgc(self) -> bool:
        """Return True if the genetic code is a physical genetic code (PGC)."""
        raise NotImplementedError("GCABC.is_pgc must be overridden")

    @abstractmethod
    def logical_mermaid_chart(self) -> str:
        """Return a Mermaid chart of the logical genetic code structure."""
        raise NotImplementedError("GCABC.logical_mermaid_chart must be overridden")

    @abstractmethod
    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the data members of the GCABC."""
        raise NotImplementedError("GCABC.set_members must be overridden")

    @abstractmethod
    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set the value of a key if it does not exist and return the set value."""
        raise NotImplementedError("GCABC.setdefault must be overridden")
