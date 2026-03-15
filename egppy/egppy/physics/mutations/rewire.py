"""The rewire module provides rewiring operations for genetic codes."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    SRC_KEY_DICT,
    DstIfKey,
    SrcIfKey,
)
from egppy.physics.mutations.common import copy_rgc, verify_graph_size
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def rewire(
    rtctxt: RuntimeContext,
    rgc: EGCode,
    dst_if_key: DstIfKey,
    dst_idx: int,
    src_if_key: SrcIfKey,
    src_idx: int,
) -> EGCode:
    """Rewire a destination endpoint to a new source endpoint.

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation verifies interface type compatibility (FR-011).

    Arguments:
        rtctxt: The runtime context.
        rgc: The genetic code to rewire.
        dst_if_key: The destination interface key.
        dst_idx: The index of the destination endpoint.
        src_if_key: The source interface key.
        src_idx: The index of the source endpoint.
    Returns:
        The rewired EGCode.
    """
    if dst_if_key[0] not in DESTINATION_ROW_SET:
        raise ValueError(f"{dst_if_key} is not a destination interface.")

    # Create a deep copy for atomicity (FR-010)
    rgc_new = copy_rgc(rgc)
    cgraph = rgc_new["cgraph"]

    dst_if = cgraph[dst_if_key]
    src_if = cgraph[src_if_key]

    if dst_idx >= len(dst_if) or src_idx >= len(src_if):
        raise IndexError("Endpoint index out of range.")

    dst_ep = dst_if[dst_idx]
    src_ep = src_if[src_idx]

    # Verify type compatibility (FR-011)
    # Allow both standard connections and downcast connections for maximum flexibility
    if not (dst_ep.can_connect(src_ep) or dst_ep.can_downcast_connect(src_ep)):
        raise TypeError(f"Incompatible interface types: {src_ep.typ} -> {dst_ep.typ}")

    # Perform rewiring: disconnect existing and connect to new
    if dst_ep.is_connected():
        _logger.debug("Rewire: Disconnecting %s[%d] from its current source", dst_if_key, dst_idx)
        # A destination endpoint has at most 1 reference (to a source)
        ref = dst_ep.refs[0]
        # Get the old source endpoint
        old_src_if_key = SRC_KEY_DICT[ref.row]
        old_src_if = cgraph[old_src_if_key]
        if old_src_if:
            old_src = old_src_if[ref.idx]
            # Remove dst_ep from old_src.refs
            for i, r in enumerate(list(old_src.refs)):
                if r.row == dst_ep.row and r.idx == dst_ep.idx:
                    del old_src.refs[i]
                    break

        # Clear dst_ep.refs
        dst_ep.clr_refs()

    _logger.debug("Rewire: Connecting %s[%d] to %s[%d]", dst_if_key, dst_idx, src_if_key, src_idx)
    dst_ep.connect(src_ep)
    src_ep.connect(dst_ep)

    # Enforce graph size limit (FR-008)
    verify_graph_size(rgc_new)

    # Defensive validation (Principle III)
    rgc_new.verify()
    rgc_new.consistency()

    return rgc_new
