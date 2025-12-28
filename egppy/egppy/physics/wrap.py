"""
Docstring for egppy.physics.insertion
"""

from enum import IntEnum

from egppy.genetic_code.c_graph_abc import CGraphABC, FrozenCGraphABC
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, SrcIfKey, SrcRow
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.interface import Interface
from egppy.physics.helpers import new_egc
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext


class WrapCase(IntEnum):
    """Enumeration of wrapping cases.
    See docs/insertion.md for details.
    """

    STACK = 0
    ISTACK = 1
    WRAP = 2
    IWRAP = 3
    HARMONY = 4


def wrap(
    rtctxt: RuntimeContext, igc: GCABC, tgc: GCABC, case: WrapCase, rgc: EGCode | None = None
) -> EGCode:
    """Wrap igc and tgc in rgc.

    rgc is modified in place.
    All connections are preserved except the connections

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: A GC.
        tgc: A GC.
        case: The wrapping case.
        rgc: The EGCode where igc and tgc will be wrapped. Created if None.
    Returns:
        The modified rgc.
    """
    # pylint: disable=arguments-out-of-order
    match case:
        case WrapCase.STACK:
            return _stack(rtctxt, igc, tgc, rgc)
        case WrapCase.ISTACK:
            return _stack(rtctxt, tgc, igc, rgc)
        case WrapCase.WRAP:
            return _wrap(rtctxt, igc, tgc, rgc)
        case WrapCase.IWRAP:
            return _wrap(rtctxt, tgc, igc, rgc)
        case WrapCase.HARMONY:
            return _harmony(rtctxt, igc, tgc, rgc)
        case _:
            raise ValueError(f"Invalid wrapping case: {case}")


def _stack(rtctxt: RuntimeContext, igc: GCABC, tgc: GCABC, rgc: EGCode | None) -> EGCode:
    """Stack tgc on top of igc.

    rgc is modified in place.
    rgc's inputs are set to tgc inputs and rgc's outputs are set to igc outputs.
    All connections in rgc are cleared.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: GCB in the rgc.
        tgc: GCA in the rgc.
        rgc: The target GC wrapping igc and tgc. Created if None.
    Returns:
        The modified rgc.
    """
    rgc = new_egc(rtctxt=rtctxt, gca=tgc, gcb=igc, rebuild=rgc)
    rgc_cgraph = rgc["cgraph"]
    assert isinstance(rgc_cgraph, CGraphABC), "tgc c_graph is not a CGraphABC"
    rgc_cgraph[SrcIfKey.IS] = Interface(rgc_cgraph[DstIfKey.AD], SrcRow.I)
    rgc_cgraph[DstIfKey.OD] = Interface(rgc_cgraph[SrcIfKey.BS], DstRow.O)
    return rgc


def _wrap(rtctxt: RuntimeContext, igc: GCABC, tgc: GCABC, rgc: EGCode | None) -> EGCode:
    """Wrap tgc (GCA) and igc (GCB) in rgc (case 2).

    rgc is modified in place.
    rgc's inputs and outputs remain the same.
    All connections in rgc are cleared.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: GCB in the rgc.
        tgc: GCA in the rgc.
        rgc: The target GC wrapping igc and tgc. Created if None.
    Returns:
        The modified rgc.
    """
    rgc = new_egc(rtctxt=rtctxt, gca=tgc, gcb=igc, rebuild=rgc)
    rgc_cgraph = rgc["cgraph"]
    rgc_cgraph[SrcIfKey.IS].clr_refs()
    rgc_cgraph[DstIfKey.OD].clr_refs()
    return rgc


def _harmony(rtctxt: RuntimeContext, gca: GCABC, gcb: GCABC, rgc: EGCode | None) -> EGCode:
    """Creates a harmony GC by placing gca and gcb in a GC but with inputs and outputs
    directly passed through (no connection between gca and gcb).

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: GCB in the rgc.
        tgc: GCA in the rgc.
        rgc: The target GC wrapping igc and tgc. Created if None.
    Returns:
        The modified rgc.
    """
    rgc = new_egc(rtctxt, gca=gca, gcb=gcb, ancestora=gca, ancestorb=gcb)
    gca_cgraph: FrozenCGraphABC = gca["cgraph"]
    gcb_cgraph: FrozenCGraphABC = gcb["cgraph"]
    gca_is_len = len(gca_cgraph[SrcIfKey.IS])
    gca_od_len = len(gca_cgraph[DstIfKey.OD])

    cgraph = rgc["cgraph"]
    cgraph[SrcIfKey.IS] = Interface(gca_cgraph[SrcIfKey.IS], SrcRow.I, DstRow.A) + Interface(
        gcb_cgraph[SrcIfKey.IS], SrcRow.I, DstRow.B
    )
    cgraph[DstIfKey.AD].set_refs(SrcRow.I)
    cgraph[SrcIfKey.AS].set_refs(DstRow.O)
    cgraph[DstIfKey.BD].set_refs(SrcRow.I, gca_is_len)
    cgraph[SrcIfKey.BS].set_refs(DstRow.O, gca_od_len)
    cgraph[DstIfKey.OD] = Interface(gca_cgraph[DstIfKey.OD], DstRow.O, SrcRow.A) + Interface(
        gcb_cgraph[DstIfKey.OD], DstRow.O, SrcRow.B
    )
    assert rgc["cgraph"].is_stable(), "Harmony resultant GC is not stable!"
    assert rgc.verify() is None, "Harmony resultant GC verification failed!"
    return rgc
