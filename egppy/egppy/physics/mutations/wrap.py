"""The wrap module provides wrapping operations for genetic codes.

Wrapping transforms a genetic code by encapsulating it within another genetic
code structure, supporting various wrapping strategies defined by WrapCase.
See docs/design/bootstrap_mutations.md for details on each case.
"""

from enum import IntEnum

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, SrcIfKey, SrcRow
from egppy.genetic_code.interface import Interface
from egppy.physics.helpers import new_egc
from egppy.physics.mutations.common import copy_rgc, verify_graph_size
from egppy.physics.pgc_api import EGCode
from egppy.physics.processes import wrap_connection_process
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


class WrapCase(IntEnum):
    """Enumeration of wrapping strategies."""

    STACK = 0  # GCA above TGC, GCB is None
    NEST = 1  # TGC becomes GCA, GCB is new
    BRANCH = 2  # TGC becomes GCA, GCB becomes another branch


def wrap(rtctxt: RuntimeContext, rgc: EGCode, igc: EGCode, case: WrapCase) -> EGCode:
    """Wrap a genetic code within another structure.

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation follows the specific WrapCase topology.

    Arguments:
        rtctxt: The runtime context.
        rgc: The target genetic code (TGC) to wrap.
        igc: The wrapping genetic code (IGC).
        case: The wrapping strategy to apply.
    Returns:
        The wrapped EGCode (RGC).
    """
    _logger.debug("Wrap: Executing case %s", case.name)
    assert not igc.is_empty(), "IGC cannot be an empty GC!"

    # Create a deep copy for atomicity (FR-010)
    rgc_new = copy_rgc(rgc)

    if case == WrapCase.STACK:
        _rgc = wrap_stack(rtctxt, igc, rgc_new)
    elif case == WrapCase.NEST:
        _rgc = wrap_nest(rtctxt, rgc_new, igc)
    elif case == WrapCase.BRANCH:
        _rgc = wrap_branch(rtctxt, rgc_new, igc)
    else:
        raise ValueError(f"Invalid wrapping case: {case}")

    # Execute Connection Process (US2)
    _logger.debug("Wrap: Executing connection process")
    _rgc = wrap_connection_process(_rgc)

    # Enforce graph size limit (FR-008)
    verify_graph_size(_rgc)

    # Defensive validation (Principle III)
    _rgc.verify()
    _rgc.consistency()

    return _rgc


def wrap_stack(rtctxt: RuntimeContext, igc: EGCode, tgc: EGCode) -> EGCode:
    """Implement STACK wrapping: igc above tgc."""
    return new_egc(rtctxt, gca=igc, gcb=tgc, ancestora=tgc)


def wrap_nest(rtctxt: RuntimeContext, tgc: EGCode, igc: EGCode) -> EGCode:
    """Implement NEST wrapping: tgc as GCA, igc as GCB."""
    return new_egc(rtctxt, gca=tgc, gcb=igc, ancestora=tgc)


def wrap_branch(rtctxt: RuntimeContext, tgc: EGCode, igc: EGCode) -> EGCode:
    """Implement BRANCH wrapping: tgc and igc as parallel branches."""
    # This often involves creating a new parent with tgc and igc as children
    rgc = new_egc(rtctxt, gca=tgc, gcb=igc, ancestora=tgc)
    cgraph = rgc["cgraph"]
    gca_cgraph = tgc["cgraph"]
    gcb_cgraph = igc["cgraph"]

    gca_is_len = len(gca_cgraph[SrcIfKey.IS])
    gcb_is_len = len(gcb_cgraph[SrcIfKey.IS])
    gca_od_len = len(gca_cgraph[DstIfKey.OD])

    # Parallel input: Is -> Ad and Is -> Bd
    cgraph[SrcIfKey.IS] = Interface(gca_cgraph[SrcIfKey.IS], SrcRow.I) + Interface(
        gcb_cgraph[SrcIfKey.IS], SrcRow.I
    )
    cgraph[DstIfKey.AD].set_refs(SrcRow.I, 0)
    cgraph[DstIfKey.BD].set_refs(SrcRow.I, gca_is_len)
    cgraph[SrcIfKey.BS].set_refs(DstRow.O, gca_od_len)
    cgraph[DstIfKey.OD] = Interface(gca_cgraph[DstIfKey.OD], DstRow.O, SrcRow.A) + Interface(
        gcb_cgraph[DstIfKey.OD], DstRow.O, SrcRow.B
    )
    return rgc
