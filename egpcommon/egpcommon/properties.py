""" "This module defines the Genetic Code properties."""

from enum import IntEnum

from bitdict import bitdict_factory, BitDictABC
from markdown import generate_markdown_tables


class GCType(IntEnum):
    """Genetic code type."""

    CODON = 0
    ORDINARY = 1
    RESERVED_2 = 2
    RESERVED_3 = 3


class CGraphType(IntEnum):
    """Graph type."""

    IF_THEN = 0
    IF_THEN_ELSE = 1
    EMPTY = 2
    FOR_LOOP = 3
    WHILE_LOOP = 4
    STANDARD = 5
    PRIMITIVE = 6
    RESERVED_7 = 7
    RESERVED_8 = 8
    RESERVED_9 = 9
    RESERVED_10 = 10
    RESERVED_11 = 11
    RESERVED_12 = 12
    RESERVED_13 = 13
    RESERVED_14 = 14
    UNKNOWN = 15  # This is not a valid connection graph type. Used when constructing graphs.


PROPERTIES_CONFIG = {
    "gc_type": {
        "type": "uint",
        "start": 0,
        "width": 2,
        "default": 0,
        "valid": {"range": [(2,)]},
        "description": ("GC type."),
    },
    "graph_type": {
        "type": "uint",
        "start": 2,
        "width": 4,
        "default": 0,
        "valid": {"range": [(7,)]},
        "description": ("Graph type."),
    },
    "reserved1": {
        "type": "uint",
        "start": 6,
        "width": 2,
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
    "abstract": {
        "type": "bool",
        "start": 10,
        "width": 1,
        "default": False,
        "description": "At least one type in one interface is abstract.",
    },
    "side_effects": {
        "type": "bool",
        "start": 11,
        "width": 1,
        "default": False,
        "description": (
            "The genetic code has side effects that are not " "related to the return value."
        ),
    },
    "static_creation": {
        "type": "bool",
        "start": 12,
        "width": 1,
        "default": False,
        "description": (
            "The genetic code was created by a deterministic PGC i.e. had no random element."
        ),
    },
    "reserved2": {
        "type": "uint",
        "start": 13,
        "width": 3,
        "default": 0,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "gctsp": {
        "type": "bitdict",
        "start": 16,
        "width": 8,
        "selector": "gc_type",
        "description": "GC type specific properties.",
        "subtype": [
            {
                "simplification": {
                    "type": "bool",
                    "start": 0,
                    "width": 1,
                    "default": False,
                    "description": (
                        "The genetic code is eligible to be simplified by symbolic regression."
                    ),
                }
            },
            {
                "literal": {
                    "type": "bool",
                    "start": 0,
                    "width": 1,
                    "default": False,
                    "description": (
                        "The codon output type is a literal (which "
                        "requires special handling in some cases)."
                    ),
                }
            },
        ],
    },
    "reserved3": {
        "type": "uint",
        "start": 24,
        "width": 40,
        "default": 0,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
}


PropertiesBD: type[BitDictABC] = bitdict_factory(
    PROPERTIES_CONFIG, "PropertiesBD", title="Genetic Code Properties"
)
PropertiesBD.__doc__ = "BitDict for Genetic Code properties."


def _verify(properties: BitDictABC) -> bool:
    """Verify the properties for consistency."""
    assert isinstance(properties, BitDictABC)

    # Make sure the properties are valid first.
    if not properties.valid():
        return False

    # If the GC is a codon then the graph cannot be empty.
    if properties["gc_type"] == GCType.CODON and properties["graph_type"] == CGraphType.EMPTY:
        return False

    # If the genetic code is constant, it must be deterministic.
    if properties["constant"] and not properties["deterministic"]:
        return False

    return True


PropertiesBD.assign_verification_function(_verify)


# Standard Property Constants
BASIC_CODON_PROPERTIES: int = PropertiesBD(
    {"gc_type": GCType.CODON, "graph_type": CGraphType.STANDARD}
).to_int()
BASIC_ORDINARY_PROPERTIES: int = PropertiesBD(
    {"gc_type": GCType.ORDINARY, "graph_type": CGraphType.STANDARD}
).to_int()

if __name__ == "__main__":
    print("\n\n".join(generate_markdown_tables(PropertiesBD)))
