"""Genetic Code Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import MutableMapping
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
MERMAID_BLUE = "dataBlue"
MERMAID_GREEN = "dataPurple"
MERMAID_RED = "dataRed"
MERMAID_BLACK = "default"
MERMAID_HEADER: list[str] = [
    "%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%",
    "flowchart TD",
]
MERMAID_FOOTER: list[str] = [
    "classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4",
    "classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff",
    "classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff",
    "classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff",
    "classDef dataRed fill:#6e4646,stroke:#8f6060,stroke-width:2px,color:#ffffff",
    "classDef dataPurple fill:#594a5c,stroke:#7b687f,stroke-width:2px,color:#ffffff",
    "classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff",
    "classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff",
    "classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff",
    "classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff",
    "classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5",
    "classDef zoneExternal fill:#221f2e,stroke:#4a3b52,stroke-width:2px,stroke-dasharray: 5 5",
    "linkStyle default stroke:#6c7a89,stroke-width:2px",
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


class GCABC(MutableMapping[str, Any], CacheableObjABC):
    """Genetic Code Abstract Base Class.

    All Genetic Code classes have a MutableMapping[str, Any] interface for getting
    and setting members. All GC keys are strings from a frozen set of keys.
    Inherits from MutableMapping to formally conform to the mapping protocol,
    which provides get, setdefault, pop, popitem, clear, update, keys, values,
    and items as mixin methods.
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
    def is_codon(self) -> bool:
        """Return True if the GCABC is a codon."""
        raise NotImplementedError("GCABC.is_codon must be overridden")

    @abstractmethod
    def is_conditional(self) -> bool:
        """Return True if the GCABC is conditional."""
        raise NotImplementedError("GCABC.is_conditional must be overridden")

    @abstractmethod
    def is_empty(self) -> bool:
        """Return True if the GCABC is empty."""
        raise NotImplementedError("GCABC.is_empty must be overridden")

    @abstractmethod
    def is_standard(self) -> bool:
        """Return True if the GCABC is standard."""
        raise NotImplementedError("GCABC.is_standard must be overridden")

    @abstractmethod
    def is_pgc(self) -> bool:
        """Return True if the genetic code is a physical genetic code (PGC)."""
        raise NotImplementedError("GCABC.is_pgc must be overridden")

    @abstractmethod
    def logical_mermaid_chart(self) -> str:
        """Return a Mermaid chart of the logical genetic code structure."""
        raise NotImplementedError("GCABC.logical_mermaid_chart must be overridden")

    @abstractmethod
    def set_members(self, gcabc: GCABC | dict[str, Any]) -> GCABC:
        """Set the data members of the GCABC."""
        raise NotImplementedError("GCABC.set_members must be overridden")
