"""The insertion module.

Defines how a insert GC (iGC) is inserted into a target GC (tGC).
"""

from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.egc_class_factory import EGCDict
from egppy.genetic_code.ggc_class_factory import GCABC
from egppy.genetic_code.interface import Interface
from egppy.physics.runtime_context import RuntimeContext


def insert_gc_case_0(
    rtctxt: RuntimeContext, tgc: GCABC, igc: GCABC, if_locked: bool = True
) -> GCABC:
    """Insert case 0: stack.

    TGC is stacked on top of IGC and stabilized.
    The resultant GC is randomly connected (constrained by if_locked)

    Args
    ----
    tgc -- the target GC
    igc -- the insert GC
    gp -- the gene pool
    if_locked -- whether the interface of the resultant GC is defined (i.e cannot be changed)

    Returns
    -------
    GCABC -- the resultant stacked GC
    """
    igc_cgraph = igc["c_graph"]
    igc_is = igc_cgraph["Is"]
    igc_od = igc_cgraph["Od"]
    tgc_cgraph = tgc["c_graph"]
    tgc_is = tgc_cgraph["Is"]
    tgc_od = tgc_cgraph["Od"]
    graph = {
        "Is": Interface(igc_is),
        "Ad": Interface(igc_is).set_row(DstRow.A).set_cls(EndPointClass.DST),
        "As": Interface(igc_od).set_row(SrcRow.A).set_cls(EndPointClass.SRC),
        "Bd": Interface(tgc_is).set_row(DstRow.B).set_cls(EndPointClass.DST),
        "Bs": Interface(tgc_od).set_row(SrcRow.B).set_cls(EndPointClass.SRC),
        "Od": Interface(tgc_od),
    }
    rgc = EGCDict(
        {
            "gca": tgc,
            "gcb": igc,
            "ancestora": tgc,
            "ancestorb": igc,
            "pgc": rtctxt.parent_pgc,
            "c_graph": CGraph(graph),
        }
    )
    assert isinstance(rgc["c_graph"], CGraph), "Resultant GC c_graph is not a CGraph"
    rgc["c_graph"].stablize(rtctxt.gpi, if_locked)
    return rgc


def insert_gc_case_1(
    rtctxt: RuntimeContext, tgc: GCABC, igc: GCABC, if_locked: bool = True
) -> GCABC:
    """Insert case 1: inverse stack."""
    return insert_gc_case_0(rtctxt, igc, tgc, if_locked)  # pylint: disable=W1114


# Insertion case aliases
stack = insert_gc_case_0
inverse_stack = insert_gc_case_1


def sca(rtctxt: RuntimeContext, tgc: GCABC, igc: GCABC) -> GCABC:
    """Implements the Spontaneous Codon Aggregation (SCA) algorithm.
    SCA consists of the following steps:
    1. Select insert case 0 (stack iGC on top of tGC).
    2. Create a GC consistent with the stack case without constraining the interfaces.
    3. Return the stable GC

    Note that SCA is *always* unlocked, i.e., the resultant GC's interface can be
    modified.
    """
    # TODO: How does PGC percolate up?
    return stack(rtctxt, tgc, igc, False)


def harmony(rtctxt: RuntimeContext, gca: GCABC, gcb: GCABC) -> GCABC:
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

    rgc = EGCDict(
        {
            "gca": gca,
            "gcb": gcb,
            "ancestora": gca,
            "ancestorb": gcb,
            "pgc": rtctxt.parent_pgc,
            "c_graph": graph,
        }
    )
    return rgc
