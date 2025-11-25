"""The primordial python module.

This module provides routines to "bootstrap" evolution by defining
python functions that can be implemented as primitive genetic codes.
See primordial_boost.py for more details.

Functions should leverage each other as much as possible to minimize
the number of primitive genetic codes required.

NOTE: It is these python functions that are definitive, i.e., they
define the behaviour that the genetic codes must implement, so it is
important that these functions are correct & thus well tested.
"""

from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.egc_class_factory import EGCDict
from egppy.genetic_code.ggc_class_factory import GCABC
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.interface_abc import InterfaceABC
from egppy.physics.helpers import merge_properties
from egppy.physics.runtime_context import RuntimeContext


def stack(rtctxt: RuntimeContext, igc: GCABC, tgc: GCABC) -> GCABC:
    """Stack two GC's such that IGC is stacked on top of TGC and the
    interface between them stablised by random connections.

    Args
    ----
    rtctxt -- the runtime context
    igc -- the insert GC (top of the stack and provides the new GC input interface)
    tgc -- the target GC (bottom of the stack and provides the new GC output interface)

    Returns
    -------
    GCABC -- the resultant stacked GC
    """
    igc_cgraph: CGraphABC = igc["cgraph"]
    igc_is: InterfaceABC = igc_cgraph["Is"]
    igc_od: InterfaceABC = igc_cgraph["Od"]
    tgc_cgraph: CGraphABC = tgc["cgraph"]
    tgc_is: InterfaceABC = tgc_cgraph["Is"]
    tgc_od: InterfaceABC = tgc_cgraph["Od"]
    cgraph = CGraph(
        {
            "Is": Interface(igc_is, SrcRow.I, DstRow.A),
            "Ad": Interface(igc_is, DstRow.A, SrcRow.I),
            "As": Interface(igc_od, SrcRow.A).clr_refs(),
            "Bd": Interface(tgc_is, DstRow.B).clr_refs(),
            "Bs": Interface(tgc_od, SrcRow.B, DstRow.O),
            "Od": Interface(tgc_od, DstRow.O, SrcRow.B),
        }
    )
    rgc = EGCDict(
        {
            "gca": igc,
            "gcb": tgc,
            "ancestora": igc,
            "ancestorb": tgc,
            "pgc": rtctxt.parent_pgc,
            "creator": rtctxt.creator,
            "properties": merge_properties(gca=igc, gcb=tgc),
            "cgraph": cgraph,
        }
    )
    return rgc


def sca(rtctxt: RuntimeContext, igc: GCABC, tgc: GCABC) -> GCABC:
    """Implements the Spontaneous Codon Aggregation (SCA) algorithm.
    SCA consists of the following steps:
    1. Find a codon - A.
    2. Find a codon - B.
    3. Stack A on B.
    4. Connect all with the input interface unlocked.
    """
    return stack(rtctxt, igc, tgc)


def perfect_stack(rtctxt: RuntimeContext, igc: GCABC, tgc: GCABC) -> GCABC:
    """Creates a perfect stack of iGC on top of tGC.

    A perfect stack is one where the interfaces of the iGC and tGC match perfectly
    and are connected directly (same index to same index) without any stabilization
    or randomization.

    Note that the compatibility of interfaces is not checked here and must be
    ensured by the caller. If the interfaces do not match, the resultant GC
    will be invalid and an execption will be raised.

    Args:
        rtctxt: The runtime context.
        igc: The insert genetic code (top of the stack).
        tgc: The target genetic code (bottom of the stack).
    Returns:
        The resultant stacked genetic code.
    """
    rgc = stack(rtctxt, igc, tgc)
    adi: Interface = rgc["cgraph"]["Ad"]
    bsi: Interface = rgc["cgraph"]["Bs"]
    adi.set_refs(DstRow.B)
    bsi.set_refs(SrcRow.A)
    return rgc


def harmony(rtctxt: RuntimeContext, gca: GCABC, gcb: GCABC) -> GCABC:
    """Creates a harmony GC by placing gca and gcb in a GC but with inputs and outputs
    directly passed through (no connection between gca and gcb).
    """
    gca_cgraph: CGraphABC = gca["cgraph"]
    gcb_cgraph: CGraphABC = gcb["cgraph"]
    gca_is_len = len(gca_cgraph["Is"])
    gca_od_len = len(gca_cgraph["Od"])

    cgraph = CGraph(
        {
            "Is": gca_cgraph["Is"] + Interface(gcb_cgraph["Is"], SrcRow.I, DstRow.B),
            "Ad": Interface(gca_cgraph["Is"].to_td(), DstRow.A, SrcRow.I),
            "As": Interface(gca_cgraph["Od"].to_td(), SrcRow.A, DstRow.O),
            "Bd": Interface(gcb_cgraph["Is"].to_td(), DstRow.B, SrcRow.I, gca_is_len),
            "Bs": Interface(gcb_cgraph["Od"].to_td(), SrcRow.B, DstRow.O, gca_od_len),
            "Od": Interface(gca_cgraph["Od"].to_td(), DstRow.O, SrcRow.A).extend(
                Interface(gcb_cgraph["Od"].to_td(), DstRow.O, SrcRow.B)
            ),
        }
    )

    rgc = EGCDict(
        {
            "gca": gca,
            "gcb": gcb,
            "ancestora": gca,
            "ancestorb": gcb,
            "pgc": rtctxt.parent_pgc,
            "creator": rtctxt.creator,
            "properties": merge_properties(gca=gca, gcb=gcb),
            "cgraph": cgraph,
        }
    )
    return rgc
