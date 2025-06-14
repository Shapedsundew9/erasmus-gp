"""The selection module.

Defines how GC's are selected based on certain criteria.
The selectors defined here are selector codons (primitives).
"""

from egpcommon.egp_rnd_gen import EGPRndGen
from egppy.gc_types.genetic_code import GCABC, NULL_GC
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.c_graph.interface import Interface


def exact_input_types_selector(gp: GenePoolInterface, seed: int, ept_types: Interface) -> GCABC:
    """Select a GC with the exact input types.

    Note that an interface is just a sequence of types and so can be used as a suitable
    set of types specifier for the search.

    Args:
        gp: The gene pool.
        seed: The random seed (this is usually the initial creation epoch)
        ept_types: The input types.

    Returns:
        A GC with the exact input types.
    """
    # Select a GC with the exact input types
    gc = gp.select_gc(ept_types)
    if gc is None:
        raise ValueError("No GC found with the exact input types.")
    return gc
