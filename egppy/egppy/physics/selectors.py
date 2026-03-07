"""The selectors module."""

from egpcommon.properties import CODON_MASK
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.genetic_code.types_def_store import types_def_store
from egppy.physics.runtime_context import RuntimeContext


def random_codon_selector(rtctxt: RuntimeContext) -> GGCDict:
    """Select a random codon from the gene pool.

    This function uses the runtime context to access the gene pool interface
    and select a random codon genetic code.

    Args:
        rtctxt: The runtime context.
    Returns:
        GGCDict: A random codon genetic code.
    """
    ggc = rtctxt.gpi.select_gc(
        "{codon_mask} & {properties} = {zero}",
        literals={"codon_mask": CODON_MASK, "zero": 0},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_pgc_selector(rtctxt: RuntimeContext) -> GGCDict:
    """Select a random PGC (mutation) from the gene pool.

    This function uses the runtime context to access the gene pool interface
    and select a random PGC (mutation) genetic code.

    Args:
        rtctxt: The runtime context.
    Returns:
        GGCDict: A random PGC (mutation) genetic code.
    """
    # Any GC returning an EGCode output type is a valid mutation candidate.
    ggc = rtctxt.gpi.select_gc(
        "{output_types} @> ARRAY[{eg_code_td}]::INT[]",
        literals={"eg_code_td": types_def_store["EGCode"]},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc
