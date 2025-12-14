"""
Docstring for egppy.physics.insertion
"""

from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.genetic_code.genetic_code import GCABC
from egppy.physics.helpers import direct_connect_interfaces, new_egc
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egpseed.primordial_python import DstRow, Interface, SrcRow


def insert(
    rtctxt: RuntimeContext, igc: GCABC, tgc: EGCode, above: DstIfKey, pc: bool = True
) -> None:
    """Insert igc into tgc above the specified destination interface.

    tgc is modified in place.
    All connection are preserved except the connections

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: The GC to be inserted.
        tgc: The target GC where igc will be inserted.
        above: The destination interface in tgc where igc will be inserted above.
        pc: Whether to preserve existing connections in tgc.
    """
    match above:
        case DstIfKey.AD:
            insert_case_3(rtctxt, igc, tgc, pc)
        case DstIfKey.BD:
            raise NotImplementedError("Insertion above BD is not yet implemented.")
        case DstIfKey.OD:
            raise NotImplementedError("Insertion above OD is not yet implemented.")
        case _:
            raise ValueError(f"Invalid destination interface key for insertion: {above}")


def insert_case_3(rtctxt: RuntimeContext, igc: GCABC, tgc: EGCode, pc: bool = True) -> None:
    """Insert igc into tgc above GCA (case 3).

    A new EGCode, fgc, is created with igc as GCA and tgc's GCA as GCB. The inputs of
    tgc are then connected to the inputs of fgc.

    tgc is modified in place.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        igc: The GC to be inserted.
        tgc: The target GC where igc will be inserted.
        pc: Whether to preserve existing connections in tgc.
    """
    fgc = new_egc(rtctxt, gca=igc, gcb=tgc["gca"], ancestora=tgc)
    fgc_cgraph = fgc["cgraph"]
    tgc_cgraph = tgc["cgraph"]
    fgc_cgraph[SrcIfKey.IS] = Interface(tgc_cgraph[DstIfKey.AD], SrcRow.I).clr_refs()
    fgc_cgraph[DstIfKey.OD] = Interface(tgc_cgraph[SrcIfKey.AS], DstRow.O).clr_refs()
    tgc["gca"] = fgc

    if pc:
        # We know FGC's input interface is the same as TGC's BD interface
        # and FGC's output interface is the same as TGC's BS interface so need
        # to check those connections.
        direct_connect_interfaces(fgc_cgraph[SrcIfKey.IS], fgc_cgraph[DstIfKey.BD], check=False)
        direct_connect_interfaces(fgc_cgraph[SrcIfKey.BS], fgc_cgraph[DstIfKey.OD], check=False)
