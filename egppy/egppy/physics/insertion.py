"""The insertion module.

Defines how a insert GC (iGC) is inserted into a target GC (tGC).
"""

from egpcommon.egp_rnd_gen import EGPRndGen
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.egc_class_factory import EGCDict
from egppy.genetic_code.ggc_class_factory import GCABC
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.interface_abc import InterfaceABC
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
    igc_cgraph: CGraphABC = igc["c_graph"]
    igc_is: InterfaceABC = igc_cgraph["Is"]
    igc_od: InterfaceABC = igc_cgraph["Od"]
    tgc_cgraph: CGraphABC = tgc["c_graph"]
    tgc_is: InterfaceABC = tgc_cgraph["Is"]
    tgc_od: InterfaceABC = tgc_cgraph["Od"]
    graph = {
        "Is": Interface(igc_is).clr_refs(),
        "Ad": Interface(igc_is).set_row(DstRow.A).set_cls(EndPointClass.DST).clr_refs(),
        "As": Interface(igc_od).set_row(SrcRow.A).set_cls(EndPointClass.SRC).clr_refs(),
        "Bd": Interface(tgc_is).set_row(DstRow.B).set_cls(EndPointClass.DST).clr_refs(),
        "Bs": Interface(tgc_od).set_row(SrcRow.B).set_cls(EndPointClass.SRC).clr_refs(),
        "Od": Interface(tgc_od).clr_refs(),
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
    rgc["c_graph"].stablize(rtctxt.gpi, if_locked, EGPRndGen(rgc["created"]))
    return rgc


def insert_gc_case_1(
    rtctxt: RuntimeContext, tgc: GCABC, igc: GCABC, if_locked: bool = True
) -> GCABC:
    """Insert case 1: inverse stack."""
    return insert_gc_case_0(rtctxt, igc, tgc, if_locked)  # pylint: disable=arguments-out-of-order


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
    return stack(rtctxt, tgc, igc, False)


def harmony(rtctxt: RuntimeContext, gca: GCABC, gcb: GCABC) -> GCABC:
    """Creates a harmony GC by placing gca and gcb in a GC but with inputs and outputs
    directly passed through (no connection between gca and gcb).
    """
    gca_cgraph: CGraphABC = gca["c_graph"]
    gca_is: InterfaceABC = gca_cgraph["Is"]
    gca_od: InterfaceABC = gca_cgraph["Od"]
    gcb_cgraph: CGraphABC = gcb["c_graph"]
    gcb_is: InterfaceABC = gcb_cgraph["Is"]
    gcb_od: InterfaceABC = gcb_cgraph["Od"]
    gca_is_len = len(gca_is)
    gca_od_len = len(gca_od)
    graph = {
        "Is": gca_is + gcb_is.ref_shift(gca_is_len),
        "Ad": gca_is.set_row(DstRow.A).set_cls(EndPointClass.DST),
        "As": gca_od.set_row(SrcRow.A).set_cls(EndPointClass.SRC),
        "Bd": gcb_is.set_row(DstRow.B).set_cls(EndPointClass.DST).ref_shift(gca_is_len),
        "Bs": gcb_od.set_row(SrcRow.B).set_cls(EndPointClass.SRC).ref_shift(gca_od_len),
        "Od": gca_od + gcb_od.ref_shift(gca_od_len),
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
