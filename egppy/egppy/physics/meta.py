"""Methods for meta codons.

Meta codons are used to manipulate the implementation of the genetic code
functions. They have no effect on the genetic code function but are used
to instrument for profiling or monitoring purposes, or to provide manipulation
of EGP's type management system.
"""

from copy import deepcopy
from typing import Any, Sequence

from egpcommon.common import EGP_EPOCH, SHAPEDSUNDEW9_UUID
from egpcommon.parallel_exceptions import create_parallel_exceptions
from egpcommon.properties import CGraphType, GCType
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import NULL_GC, GGCDict
from egppy.genetic_code.types_def import TypesDef, types_def_store
from egppy.physics.runtime_context import RuntimeContext

META_CODON_TEMPLATE: dict[str, Any] = {
    "code_depth": 1,
    "gca": None,
    "gcb": None,
    "ancestora": None,
    "ancestorb": None,
    "pgc": None,
    "generation": 1,
    "num_codes": 1,
    "num_codons": 1,
    "creator": SHAPEDSUNDEW9_UUID,
    "created": EGP_EPOCH.isoformat(),
    "properties": {
        "gc_type": GCType.META,
        "graph_type": CGraphType.PRIMITIVE,
        "constant": False,
        "deterministic": True,
        "side_effects": False,
        "static_creation": True,
        "gctsp": {"type_upcast": True, "type_downcast": False},
    },
    "meta_data": {
        "function": {
            "python3": {
                "0": {
                    "inline": "tuple(raise_if_not_instance_of(ix, tx) for ix, tx in zip({i}, {t}))",
                    "description": "Raise if ix is not an instance or child of tx.",
                    "name": "raise_if_not_instance_of(ix, tx)",
                    "imports": [
                        {
                            "aip": ["egppy", "physics", "meta"],
                            "name": "raise_if_not_instance_of",
                        }
                    ],
                }
            }
        }
    },
}

# Create a module with parallel exceptions for meta codons
MetaCodonExceptionModule = create_parallel_exceptions(
    prefix="MetaCodon", module_name="egppy.worker.executor.meta_codons"
)

# Find some common exceptions in the module
MetaCodonError = MetaCodonExceptionModule.get_parallel_equivalent(Exception)
MetaCodonValueError = MetaCodonExceptionModule.get_parallel_equivalent(ValueError)
MetaCodonTypeError = MetaCodonExceptionModule.get_parallel_equivalent(TypeError)


def meta_upcast(rtctxt: RuntimeContext, tsa: Sequence[TypesDef], tsb: Sequence[TypesDef]) -> GCABC:
    """Find or create a meta-codon that upcasts ifa types to exactly match ifb types.

    ifb must have the same length as ifa and each type in ifb must a descendent of the
    corresponding type in ifa.

    Example
    -------
    Suppose we have two interfaces:
        ifa: [int, float, object]
        ifb: [Integral, float, str]
    Then the meta genetic code will be one that casts:
        tsa = [object] -> tsb = [str]
    as Integral is an ancestor of int and float is already the same type in both interfaces.

    Args:
        rtctxt: The runtime context.
        tsa: The type sequence to cast from.
        tsb: The type sequence to cast to.
    Returns:
        A meta genetic code that perform the appropriate casting for endpoints that need it.
        Note that the order of casts is independent of the order in tsa and tsb.

    """
    # The implementation tries to find existing meta genetic codes that perform the required casts.
    # If none exist, a new one is created.
    pts: tuple[tuple[TypesDef, TypesDef], ...] = tuple(zip(tsa, tsb))
    assert [
        pt for pt in pts if pt[1] not in types_def_store.ancestors(pt[0])
    ], "Invalid type upcast requested."
    mgc = rtctxt.gpi.select_meta(pts)
    if mgc is not NULL_GC:
        return mgc

    # No existing meta cast found - create a new one
    return GGCDict(
        deepcopy(META_CODON_TEMPLATE)
        | {
            # Passing in as a JSONCGraph which will get converted to a CGraph in EGCDict
            "cgraph": {
                "A": [["I", i, pt[0].name] for i, pt in enumerate(pts)],
                "O": [["A", i, pt[1].name] for i, pt in enumerate(pts)],
            },
        }
    )


def raise_if_not_instance_of(obj: Any, t: type) -> Any:
    """Raise an error if the object is not an instance of the given types."""
    if not isinstance(obj, t):
        raise MetaCodonTypeError(f"Expected {t}, got {type(obj)} instead.")
    return obj
