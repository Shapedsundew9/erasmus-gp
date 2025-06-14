"""The insertion module.

Defines how a insert GC (iGC) is inserted into a target GC (tGC).
"""

from random import randint

from egppy.gc_types.egc_class_factory import EGCDirtyDict
from egppy.gc_types.genetic_code import GCABC
from egppy.gene_pool.gene_pool_interface import GenePoolInterface


def insert_gc_case_0(tgc: GCABC, igc: GCABC, gp: GenePoolInterface, empty: bool = True) -> GCABC:
    """Insert case 0: stack.

    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    empty -- whether the interface of the resultant GC is defined (i.e cannot be changed)
    """
    graph = {
        "Is": igc["Is"],
        "Ad": igc["Is"],
        "As": igc["Od"],
        "Bd": tgc["Is"],
        "Bs": tgc["Od"],
        "Od": tgc["Od"],
    }
    rgc = EGCDirtyDict(
        {"gca": tgc, "gcb": igc, "ancestora": tgc, "ancestorb": igc, "c_graph": graph}
    )

    return rgc["c_graph"].stablize(gp, empty)


def insert_gc_case_1(tgc: GCABC, igc: GCABC, gp: GenePoolInterface, empty: bool = True) -> GCABC:
    """Insert case 1: inverse stack.

    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    empty -- whether the interface of the resultant GC is defined (i.e cannot be changed)
    """
    rgc = EGCDirtyDict({"gca": igc, "gcb": tgc, "ancestora": igc, "ancestorb": tgc})
    return rgc["c_graph"].stablize(gp, empty)


# Interation case aliases
stack = insert_gc_case_0
inverse_stack = insert_gc_case_1


def sca(tgc: GCABC, igc: GCABC, gp: GenePoolInterface) -> GCABC:
    """Implements the Spontaneous Codon Aggregation (SCA) algorithm.
    SCA consists of the following steps:
    1. Select insert case 0 (stack) or insert case 1 (inverse stack) randomly.
    2. Create a GC consistent with the stack case without constraining the interfaces.
    3. Return the stable GC
    """
    return stack(tgc, igc, gp, False) if randint(0, 1) else inverse_stack(tgc, igc, gp, False)
