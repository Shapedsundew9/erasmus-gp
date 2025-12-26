"""
Docstring for egppy.physics.insertion
"""

from enum import IntEnum

from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, IfKey, SrcIfKey, SrcRow
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.interface import Interface
from egppy.physics.helpers import direct_connect_interfaces, new_egc
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext


class InsertionCase(IntEnum):
    """Enumeration of insertion cases.
    See docs/insertion.md for details.
    """

    ABOVE_A = 0
    ABOVE_B = 1
    ABOVE_O = 2


def insert(rtctxt: RuntimeContext, igc: GCABC, tgc: EGCode, case: InsertionCase | IfKey) -> EGCode:
    """Insert igc into tgc above the specified destination interface.

    See docs/insertion.md for details.
    tgc is modified in place (i.e. tgc is rgc after insertion).
    All connections are preserved except the connections

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: The GC to be inserted.
        tgc: The target GC where igc will be inserted.
        case: The insertion case or the interface in tgc where igc will be
              inserted. If it is a destination interface key igc will be inserted
              immediately above that interface, if it is a source interface key
              it will be inserted immediately below that interface.
    Returns:
        The modified tgc (rgc).
    """
    assert isinstance(tgc, EGCode), "Target GC is not an EGCode - it cannot be modified in place."

    match case:
        case SrcIfKey.IS | DstIfKey.AD | InsertionCase.ABOVE_A:
            return insert_above_a(rtctxt, igc, tgc)
        case SrcIfKey.AS | DstIfKey.BD | InsertionCase.ABOVE_B:
            return insert_above_b(rtctxt, igc, tgc)
        case SrcIfKey.BS | DstIfKey.OD | InsertionCase.ABOVE_O:
            return insert_above_o(rtctxt, igc, tgc)
        case _:
            raise ValueError(f"Invalid destination interface key for insertion: {case}")


def insert_above_a(rtctxt: RuntimeContext, igc: GCABC, tgc: EGCode) -> EGCode:
    """Insert igc into tgc above GCA (case 3).

    A new EGCode, fgc, is created with igc as GCA and tgc's GCA as GCB. tgc's GCA
    is set to fgc. The inputs of tgc are then connected to the inputs of fgc.

    tgc is modified in place.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: The GC to be inserted.
        tgc: The target GC where igc will be inserted.
    Returns:
        The modified tgc (rgc).
    """
    fgc = new_egc(rtctxt, gca=igc, gcb=tgc["gca"], ancestora=tgc)
    fgc_cgraph = fgc["cgraph"]
    tgc_cgraph = tgc["cgraph"]
    fgc_cgraph[SrcIfKey.IS] = Interface(tgc_cgraph[DstIfKey.AD], SrcRow.I).clr_refs()
    fgc_cgraph[DstIfKey.OD] = Interface(tgc_cgraph[SrcIfKey.AS], DstRow.O).clr_refs()
    tgc["gca"] = fgc

    # We know FGC's input interface is the same as TGC's BD interface
    # and FGC's output interface is the same as TGC's BS interface so no need
    # to check those connections.
    direct_connect_interfaces(fgc_cgraph[SrcIfKey.IS], fgc_cgraph[DstIfKey.BD], check=False)
    direct_connect_interfaces(fgc_cgraph[SrcIfKey.BS], fgc_cgraph[DstIfKey.OD], check=False)
    return tgc


def insert_above_b(rtctxt: RuntimeContext, igc: GCABC, tgc: EGCode) -> EGCode:
    """Insert igc into tgc above GCB (case 4).

    A new EGCode, fgc, is created with tgc's GCB as GCB and igc as GCA. tgc's GCB
    is set to fgc. The inputs of tgc are then connected to the inputs of fgc and fgc's
    outputs.

    tgc is modified in place.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: The GC to be inserted.
        tgc: The target GC where igc will be inserted.
    Returns:
        The modified tgc (rgc).
    """
    fgc = new_egc(rtctxt, gca=igc, gcb=tgc["gcb"], ancestora=tgc)
    fgc_cgraph = fgc["cgraph"]
    tgc_cgraph = tgc["cgraph"]
    fgc_cgraph[SrcIfKey.IS] = Interface(tgc_cgraph[DstIfKey.BD], SrcRow.I).clr_refs()
    fgc_cgraph[DstIfKey.OD] = Interface(tgc_cgraph[SrcIfKey.BS], DstRow.O).clr_refs()
    tgc["gcb"] = fgc

    # We know FGC's input interface is the same as TGC's BD interface
    # and FGC's output interface is the same as TGC's BS interface so no need
    # to check those connections.
    direct_connect_interfaces(fgc_cgraph[SrcIfKey.IS], fgc_cgraph[DstIfKey.BD], check=False)
    direct_connect_interfaces(fgc_cgraph[SrcIfKey.BS], fgc_cgraph[DstIfKey.OD], check=False)
    return tgc


def insert_above_o(rtctxt: RuntimeContext, igc: GCABC, tgc: EGCode) -> EGCode:
    """Insert igc into tgc above Output (case 5).

    A new EGCode, fgc, is created with tgc's GCB as GCA and igc as GCB. tgc's GCB
    is set to fgc. The inputs of tgc are then connected to the inputs of fgc.
    tgc is modified in place.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: The GC to be inserted.
        tgc: The target GC where igc will be inserted.
    Returns:
        The modified tgc (rgc).
    """
    fgc = new_egc(rtctxt, gca=igc, gcb=tgc["gcb"], ancestora=tgc)
    fgc_cgraph = fgc["cgraph"]
    tgc_cgraph = tgc["cgraph"]
    fgc_cgraph[SrcIfKey.IS] = Interface(tgc_cgraph[DstIfKey.OD], SrcRow.I).clr_refs()
    fgc_cgraph[DstIfKey.OD] = Interface(tgc_cgraph[SrcIfKey.BS], DstRow.O).clr_refs()
    tgc["gcb"] = fgc

    # We know FGC's input interface is the same as TGC's BD interface
    # and FGC's output interface is the same as TGC's BS interface so no need
    # to check those connections.
    direct_connect_interfaces(fgc_cgraph[SrcIfKey.IS], fgc_cgraph[DstIfKey.AD], check=False)
    direct_connect_interfaces(fgc_cgraph[SrcIfKey.AS], fgc_cgraph[DstIfKey.OD], check=False)
    return tgc
