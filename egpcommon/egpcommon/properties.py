""" "This module defines the Genetic Code properties."""

from enum import IntEnum

from bitdict import BitDictABC, bitdict_factory
from bitdict.markdown import generate_markdown_tables


class GCType(IntEnum):
    """Genetic code type."""

    CODON = 0
    ORDINARY = 1
    META = 2
    ORDINARY_META = 3


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
    UNKNOWN = 15  # The common subset


PROPERTIES_CONFIG = {
    "gc_type": {
        "type": "uint",
        "start": 0,
        "width": 3,
        "valid": {"range": [(4,)]},
        "default": 0,
        "description": ("GC type."),
    },
    "graph_type": {
        "type": "uint",
        "start": 3,
        "width": 4,
        "default": 0,
        "valid": {"range": [(7,)]},
        "description": ("Graph type."),
    },
    "reserved1": {
        "type": "uint",
        "start": 7,
        "width": 1,
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
    # TODO: Why do we care about 'abstract'? Currently not used (as expensive to compute).
    # May be just a codon property?
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
            "The genetic code has side effects in the execution "
            "context that are not related to the return value e.g. modifying global state "
            "like a random sequence generator or storing to memory etc."
        ),
    },
    # TODO: Is this needed? Tells use we can deterministically create the GC again but that should
    # be the case for all GC's if we have a standard way of determining the seed unique the the
    # creation instance (e.g. parent PGC id + time etc).
    "static_creation": {
        "type": "bool",
        "start": 12,
        "width": 1,
        "default": False,
        "description": (
            "The genetic code was created by a deterministic PGC i.e. had no random element."
        ),
    },
    "is_pgc": {
        "type": "bool",
        "start": 13,
        "width": 1,
        "default": False,
        "description": "The genetic code is a physical genetic code "
        "(PGC) i.e. it creates a new GC.",
    },
    "reserved2": {
        "type": "uint",
        "start": 14,
        "width": 2,
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
                },
                "reserved7": {
                    "type": "uint",
                    "start": 1,
                    "width": 5,
                    "default": 0,
                    "description": "Reserved for future use.",
                    "valid": {"value": {0}},
                },
                "python": {
                    "type": "bool",
                    "start": 6,
                    "width": 1,
                    "default": True,
                    "description": "Codon code is Python.",
                },
                "psql": {
                    "type": "bool",
                    "start": 7,
                    "width": 1,
                    "default": False,
                    "description": "Codon code is Postgres flavoured SQL.",
                },
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
                },
                "reserved6": {
                    "type": "uint",
                    "start": 1,
                    "width": 5,
                    "default": 0,
                    "description": "Reserved for future use.",
                    "valid": {"value": {0}},
                },
                "python": {
                    "type": "bool",
                    "start": 6,
                    "width": 1,
                    "default": True,
                    "description": "Codon code is Python.",
                },
                "psql": {
                    "type": "bool",
                    "start": 7,
                    "width": 1,
                    "default": False,
                    "description": "Codon code is Postgres flavoured SQL.",
                },
            },
            {
                "type_upcast": {
                    "type": "bool",
                    "start": 0,
                    "width": 1,
                    "default": False,
                    "description": (
                        "The meta codon is a type upcast e.g. Integral "
                        "--> int which means it must be verified."
                    ),
                },
                "type_downcast": {
                    "type": "bool",
                    "start": 1,
                    "width": 1,
                    "default": True,
                    "description": (
                        "The meta codon is a type downcast e.g. "
                        "int --> Integral which is always valid."
                    ),
                },
                "reserved8": {
                    "type": "uint",
                    "start": 2,
                    "width": 6,
                    "default": 0,
                    "description": "Reserved for future use.",
                    "valid": {"value": {0}},
                },
            },
            {
                "type_upcast": {
                    "type": "bool",
                    "start": 0,
                    "width": 1,
                    "default": False,
                    "description": (
                        "The meta codon is a type upcast e.g. Integral "
                        "--> int which means it must be verified."
                    ),
                },
                "type_downcast": {
                    "type": "bool",
                    "start": 1,
                    "width": 1,
                    "default": True,
                    "description": (
                        "The meta codon is a type downcast e.g. "
                        "int --> Integral which is always valid."
                    ),
                },
                "reserved8": {
                    "type": "uint",
                    "start": 2,
                    "width": 6,
                    "default": 0,
                    "description": "Reserved for future use.",
                    "valid": {"value": {0}},
                },
            },
        ],
    },
    "consider_cache": {
        "type": "bool",
        "start": 24,
        "width": 1,
        "default": False,
        "description": (
            "Runtime property. "
            "The genetic code is eligible for result caching. e.g. with the functool `lru_cache`."
            "Runtime profiling and resource availability will determine if it is actually cached."
        ),
    },
    "reserved3": {
        "type": "uint",
        "start": 25,
        "width": 7,
        "default": 0,
        "description": "Reserved for future 'Runtime properties'.",
        "valid": {"value": {0}},
    },
    "reserved4": {
        "type": "uint",
        "start": 32,
        "width": 16,
        "default": 0,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "useless": {
        "type": "bool",
        "start": 56,
        "width": 1,
        "default": False,
        "description": (
            "Codon management system property. Useless codons can be removed with "
            "no functional impact. They can occur through mutation and be difficult to spot."
        ),
        "valid": {"value": {0}},
    },
    "reserved5": {
        "type": "uint",
        "start": 57,
        "width": 7,
        "default": 0,
        "description": "Reserved for future codon management use.",
        "valid": {"value": {0}},
    },
}


PropertiesBD: type = bitdict_factory(
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
    {"gc_type": GCType.CODON, "graph_type": CGraphType.PRIMITIVE}
).to_int()
BASIC_ORDINARY_PROPERTIES: int = PropertiesBD(
    {"gc_type": GCType.ORDINARY, "graph_type": CGraphType.STANDARD}
).to_int()

if __name__ == "__main__":
    print("\n\n".join(generate_markdown_tables(PropertiesBD)))


# TODO: This mask should be generated programmatically by BitDict
# If the propoerty is a codon then it does not matter what any
# bit values are other that the LSb.
CODON_MASK: int = 0x0000000000000001
GC_TYPE_MASK: int = 0x0000000000000007
