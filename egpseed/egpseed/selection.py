"""The selection module.

Defines how GC's are selected based on certain criteria.
The selectors defined here are selector codons (primitives).
"""

from egpcommon.properties import CODON_MASK
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.ggc_dict import GCABC, GGCDict
from egppy.genetic_code.interface import Interface

# Constants
_CODON_SELECTOR_LITERALS = {"mask": CODON_MASK}


def exact_input_types_selector(gp: GenePoolInterface, _: int, ept_types: Interface) -> GCABC:
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
    its, inpts = ept_types.types_and_indices()
    gc = gp.select(
        "{input_types} = {its} AND {inputs} = {inpts}", literals={"its": its, "inpts": inpts}
    )
    if not gc:
        raise ValueError("No GC found with the exact input types.")
    return GGCDict(gc[0])


def random_codon_selector(gp: GenePoolInterface) -> GCABC:
    """Select a codon GC randomly from the gene pool."""
    gc = gp.select("NOT ({properties} & {mask})", literals=_CODON_SELECTOR_LITERALS)
    if not gc:
        raise ValueError("No codons found. Has the gene pool been initialized?")
    return GGCDict(gc[0])
