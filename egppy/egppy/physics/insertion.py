"""The insertion module.

Defines how a insert GC (iGC) is inserted into a target GC (tGC).
"""

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.egc_class_factory import EGCDict
from egppy.genetic_code.ggc_class_factory import GCABC


def insert_gc_case_0(
    tgc: GCABC, igc: GCABC, gp: GenePoolInterface, if_locked: bool = True
) -> GCABC:
    """Insert case 0: stack.

    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    if_locked -- whether the interface of the resultant GC is defined (i.e cannot be changed)
    """
    graph = {
        "Is": igc["Is"],
        "Ad": igc["Is"],
        "As": igc["Od"],
        "Bd": tgc["Is"],
        "Bs": tgc["Od"],
        "Od": tgc["Od"],
    }
    rgc = EGCDict({"gca": tgc, "gcb": igc, "ancestora": tgc, "ancestorb": igc, "c_graph": graph})
    rgc["c_graph"].stablize(gp, if_locked)
    return rgc


def insert_gc_case_1(
    tgc: GCABC, igc: GCABC, gp: GenePoolInterface, if_locked: bool = True
) -> GCABC:
    """Insert case 1: inverse stack.

    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    if_locked -- whether the interface of the resultant GC is defined (i.e cannot be changed)
    """
    return insert_gc_case_0(igc, tgc, gp, if_locked)  # pylint: disable=W1114


# Interation case aliases
stack = insert_gc_case_0
inverse_stack = insert_gc_case_1


def sca(tgc: GCABC, igc: GCABC, gp: GenePoolInterface) -> GCABC:
    """Implements the Spontaneous Codon Aggregation (SCA) algorithm.
    SCA consists of the following steps:
    1. Select insert case 0 (stack).
    2. Create a GC consistent with the stack case without constraining the interfaces.
    3. Return the stable GC
    """
    return stack(tgc, igc, gp, False)
