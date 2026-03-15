"""The insertion module provides insertion operations for genetic codes.

Insertion transforms a genetic code by inserting one genetic code into another,
supporting various insertion strategies defined by InsertionCase.
See docs/design/bootstrap_mutations.md for details on each case.
"""

from enum import IntEnum

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, SrcIfKey, SrcRow
from egppy.genetic_code.interface import Interface
from egppy.physics.helpers import direct_connect_interfaces, new_egc
from egppy.physics.mutations.common import copy_rgc, verify_graph_size
from egppy.physics.pgc_api import EGCode
from egppy.physics.processes import insert_connection_process
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


class InsertionCase(IntEnum):
    """Enumeration of insertion strategies."""

    ABOVE_A = 0  # GCA above existing GCA
    ABOVE_B = 1  # GCA above existing GCB
    BELOW_A = 2  # GCA below existing GCA
    BELOW_B = 3  # GCA below existing GCB


def insert(rtctxt: RuntimeContext, rgc: EGCode, igc: EGCode, case: InsertionCase) -> EGCode:
    """Insert a genetic code into another structure.

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation follows the specific InsertionCase topology.

    Arguments:
        rtctxt: The runtime context.
        rgc: The target genetic code (TGC) to modify.
        igc: The genetic code to insert (IGC).
        case: The insertion strategy to apply.
    Returns:
        The modified EGCode (RGC).
    """
    _logger.debug("Insert: Executing case %s", case.name)
    assert not igc.is_empty(), "IGC cannot be an empty GC!"

    # Create a deep copy for atomicity (FR-010)
    rgc_new = copy_rgc(rgc)

    if case == InsertionCase.ABOVE_A:
        _rgc = insert_above_a(rtctxt, igc, rgc_new)
    elif case == InsertionCase.ABOVE_B:
        _rgc = insert_above_b(rtctxt, igc, rgc_new)
    elif case == InsertionCase.BELOW_A:
        _rgc = insert_below_a(rtctxt, igc, rgc_new)
    elif case == InsertionCase.BELOW_B:
        _rgc = insert_below_b(rtctxt, igc, rgc_new)
    else:
        raise ValueError(f"Invalid destination interface key for insertion: {case}")

    # Execute Connection Process (US2)
    _logger.debug("Insert: Executing connection process")
    _rgc = insert_connection_process(_rgc)

    # Enforce graph size limit (FR-008)
    verify_graph_size(_rgc)

    # Defensive validation (Principle III)
    _rgc.verify()
    _rgc.consistency()

    return _rgc


def insert_above_a(rtctxt: RuntimeContext, igc: EGCode, tgc: EGCode) -> EGCode:
    """Implement insertion above GCA: IGC becomes new parent of TGC's GCA."""
    fgc = new_egc(rtctxt, gca=igc, gcb=tgc["gca"], ancestora=tgc)
    tgc["gca"] = fgc
    return tgc


def insert_above_b(rtctxt: RuntimeContext, igc: EGCode, tgc: EGCode) -> EGCode:
    """Implement insertion above GCB: IGC becomes new parent of TGC's GCB."""
    fgc = new_egc(rtctxt, gca=igc, gcb=tgc["gcb"], ancestora=tgc)
    tgc["gcb"] = fgc
    return tgc


def insert_below_a(rtctxt: RuntimeContext, igc: EGCode, tgc: EGCode) -> EGCode:
    """Implement insertion below GCA: IGC becomes GCA of a new GCA."""
    tgc_cgraph = tgc["cgraph"]
    fgc_cgraph = igc["cgraph"]
    tgc["gca"] = new_egc(rtctxt, gca=tgc["gca"], gcb=igc, ancestora=tgc)
    tgc_cgraph[DstIfKey.AD] = Interface(tgc_cgraph[DstIfKey.AD], DstRow.A).clr_refs()
    tgc_cgraph[SrcIfKey.AS] = Interface(fgc_cgraph[DstIfKey.OD], SrcRow.A).clr_refs()
    tgc["gca"] = igc

    direct_connect_interfaces(tgc_cgraph[SrcIfKey.IS], tgc_cgraph[DstIfKey.AD], check=False)
    direct_connect_interfaces(tgc_cgraph[SrcIfKey.AS], tgc_cgraph[DstIfKey.OD], check=False)
    return tgc


def insert_below_b(rtctxt: RuntimeContext, igc: EGCode, tgc: EGCode) -> EGCode:
    """Implement insertion below GCB: IGC becomes GCA of a new GCB."""
    tgc_cgraph = tgc["cgraph"]
    fgc_cgraph = igc["cgraph"]
    tgc["gcb"] = new_egc(rtctxt, gca=tgc["gcb"], gcb=igc, ancestora=tgc)
    tgc_cgraph[DstIfKey.BD] = Interface(tgc_cgraph[DstIfKey.BD], DstRow.B).clr_refs()
    tgc_cgraph[SrcIfKey.BS] = Interface(fgc_cgraph[DstIfKey.OD], SrcRow.B).clr_refs()
    tgc["gcb"] = igc

    direct_connect_interfaces(tgc_cgraph[SrcIfKey.IS], tgc_cgraph[DstIfKey.AD], check=False)
    direct_connect_interfaces(tgc_cgraph[SrcIfKey.AS], tgc_cgraph[DstIfKey.OD], check=False)
    return tgc
