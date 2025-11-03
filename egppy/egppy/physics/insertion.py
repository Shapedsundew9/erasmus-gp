"""The insertion module.

Defines how a insert GC (iGC) is inserted into a target GC (tGC).
"""

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.egc_class_factory import EGCDict
from egppy.genetic_code.ggc_class_factory import GCABC


def insert_gc_case_0(
    gp: GenePoolInterface, tgc: GCABC, igc: GCABC, if_locked: bool = True
) -> GCABC:
    """Insert case 0: stack.

    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    if_locked -- whether the interface of the resultant GC is defined (i.e cannot be changed)
    """
    graph = {
        "Is": igc["Is"].copy(True),
        "Ad": igc["Is"].copy(True),
        "As": igc["Od"].copy(True),
        "Bd": tgc["Is"].copy(True),
        "Bs": tgc["Od"].copy(True),
        "Od": tgc["Od"].copy(True),
    }
    rgc = EGCDict({"gca": tgc, "gcb": igc, "ancestora": tgc, "ancestorb": igc, "c_graph": graph})
    rgc["c_graph"].stablize(gp, if_locked)
    return rgc


def insert_gc_case_1(
    gp: GenePoolInterface, tgc: GCABC, igc: GCABC, if_locked: bool = True
) -> GCABC:
    """Insert case 1: inverse stack.

    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    if_locked -- whether the interface of the resultant GC is defined (i.e cannot be changed)
    """
    return insert_gc_case_0(gp, igc, tgc, if_locked)  # pylint: disable=W1114


# Interation case aliases
stack = insert_gc_case_0
inverse_stack = insert_gc_case_1


def sca(gp: GenePoolInterface, tgc: GCABC, igc: GCABC) -> GCABC:
    """Implements the Spontaneous Codon Aggregation (SCA) algorithm.
    SCA consists of the following steps:
    1. Select insert case 0 (stack iGC on top of tGC).
    2. Create a GC consistent with the stack case without constraining the interfaces.
    3. Return the stable GC

    Note that SCA is *always* unlocked, i.e., the resultant GC's interface can be
    modified.
    """
    # TODO: How does PGC percolate up?
    return stack(gp, tgc, igc, False)


def harmony(_: GenePoolInterface, gca: GCABC, gcb: GCABC) -> GCABC:
    """Creates a harmony GC by placing gca and gcb in a GC but with inputs and outputs
    directly passed through (no connection between gca and gcb).
    """
    graph = {
        "Is": gca["Is"] + gcb["Is"],
        "Ad": gca["Is"].copy(),
        "As": gca["Od"].copy(),
        "Bd": gcb["Is"].copy(),
        "Bs": gcb["Od"].copy(),
        "Od": gca["Od"] + gcb["Od"],
    }

    rgc = EGCDict({"gca": gca, "gcb": gcb, "ancestora": gca, "ancestorb": gcb, "c_graph": graph})
    return rgc
