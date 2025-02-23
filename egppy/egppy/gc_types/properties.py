""""This module defines the Genetic Code properties."""

from enum import IntEnum

from bitdict import bitdict_factory
from markdown import generate_markdown_tables


class GraphType(IntEnum):
    """Graph type."""

    CODON = 0
    CONDITIONAL = 1
    EMPTY = 2
    STANDARD = 3


PROPERTIES_CONFIG = {
    "graph_type": {
        "type": "uint",
        "start": 0,
        "width": 4,
        "default": 0,
        "valid": {"range": [(4,)]},
        "description": (
            "Graph type. 0 = Codon, 1 = Conditional, 2 = Empty, 3 = Standard, 4-15 = Reserved."
        ),
    },
    "reserved1": {
        "type": "uint",
        "start": 4,
        "width": 4,
        "default": 0,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "constant": {
        "type": "bool",
        "start": 8,
        "width": 1,
        "default": False,
        "description": "Genetic code _always_ returns the same result.",
    },
    "deterministic": {
        "type": "bool",
        "start": 9,
        "width": 1,
        "default": True,
        "description": (
            "Given the same inputs the genetic code will _always_ return the same result."
        ),
    },
    "simplification": {
        "type": "bool",
        "start": 10,
        "width": 1,
        "default": False,
        "description": "The genetic code is eligible to be simplified by symbolic regression.",
    },
    "literal": {
        "type": "bool",
        "start": 11,
        "width": 1,
        "default": False,
        "description": (
            "The output types are literals (which require special handling in some cases)."
        ),
    },
    "abstract": {
        "type": "bool",
        "start": 12,
        "width": 1,
        "default": False,
        "description": "At least one type in one interface is abstract.",
    },
    "reserved2": {
        "type": "uint",
        "start": 13,
        "width": 51,
        "default": 0,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
}

PropertiesBD: type = bitdict_factory(
    PROPERTIES_CONFIG, "PropertiesBD", title="Genetic Code Properties"
)
PropertiesBD.__doc__ = "BitDict for Genetic Code properties."


if __name__ == "__main__":
    print("\n\n".join(generate_markdown_tables(PropertiesBD)))
