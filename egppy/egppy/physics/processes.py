"""Connection Processes for structural mutations."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, DstRow, SrcRow, SRC_KEY_DICT
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.interface import Interface
from egppy.physics.pgc_api import EGCode

# Logging setup
_logger: Logger = egp_logger(name=__name__)

# Primary Source Mapping (FR-003)
# Key: Destination Interface, Value: Primary Source Interface
PRIMARY_SOURCES: dict[DstIfKey, SrcIfKey] = {
    DstIfKey.AD: SrcIfKey.IS,
    DstIfKey.BD: SrcIfKey.AS,
    DstIfKey.OD: SrcIfKey.BS,
}


def force_primary(rgc: EGCode, dst_if_key: DstIfKey, overwrite: bool = False) -> None:
    """Establish primary connection for a destination interface.

    Following the logic:
    1. Select compatible primary source endpoint.
    2. If no compatible connection exists, select valid primary source endpoint.
    3. If connection can be established, create it.
    4. If overwrite is True, sever existing non-primary connections first.
    """
    cgraph = rgc["cgraph"]
    src_if_key = PRIMARY_SOURCES.get(dst_if_key)
    if not src_if_key:
        return

    src_if = cgraph[src_if_key]
    dst_if = cgraph[dst_if_key]

    if not src_if or not dst_if:
        return

    # If overwrite is True, we may need to sever existing connections
    # to make room for primary ones.
    if overwrite:
        for dst_ep in dst_if:
            # We only sever if the existing connection is NOT from the primary source
            if dst_ep.is_connected():
                ref = dst_ep.refs[0]
                if ref.row != src_if_key[0]:
                    _logger.debug("Severing non-primary connection for %s", dst_if_key)
                    # Find and update old source
                    old_src_if = cgraph[SRC_KEY_DICT[ref.row]]
                    if old_src_if:
                        old_src = old_src_if[ref.idx]
                        for i, r in enumerate(list(old_src.refs)):
                            if r.row == dst_ep.row and r.idx == dst_ep.idx:
                                del old_src.refs[i]
                                break
                    dst_ep.clr_refs()

    # Attempt compatible connections first
    for src_ep, dst_ep in zip(src_if, dst_if):
        if not dst_ep.is_connected() and dst_ep.can_connect(src_ep):
            dst_ep.connect(src_ep)
            src_ep.connect(dst_ep)

    # Attempt downcast/valid connections if still unconnected
    for src_ep, dst_ep in zip(src_if, dst_if):
        if not dst_ep.is_connected() and dst_ep.can_downcast_connect(src_ep):
            dst_ep.connect(src_ep)
            src_ep.connect(dst_ep)


def create_connection_process(rgc: EGCode) -> EGCode:
    """Implement connection processing for create cases."""
    # Create order: Ad, Bd, Od
    for dst_key in [DstIfKey.AD, DstIfKey.BD, DstIfKey.OD]:
        force_primary(rgc, dst_key)
    return rgc


def wrap_connection_process(rgc: EGCode) -> EGCode:
    """Implement connection processing for wrap cases."""
    # Wrap order: Ad, Bd, Od, only if unconnected and no primary present
    for dst_key in [DstIfKey.AD, DstIfKey.BD, DstIfKey.OD]:
        iface = rgc["cgraph"][dst_key]
        if iface and any(not ep.is_connected() for ep in iface):
            force_primary(rgc, dst_key)
    return rgc


def insert_connection_process(rgc: EGCode) -> EGCode:
    """Implement connection processing for insertion cases.

    Insertion prioritizes routing existing flow through the new IGC.
    We use force_primary with overwrite=True for the relevant interfaces.
    """
    # For insertion, we ensure primary connections are established even if they overwrite.
    for dst_key in [DstIfKey.AD, DstIfKey.BD, DstIfKey.OD]:
        force_primary(rgc, dst_key, overwrite=True)
    return rgc


def update_interface_from_gc(rgc: EGCode, dst_key: DstIfKey, src_key: SrcIfKey, sub_gc: GCABC | bytes | None) -> bool:
    """Update interfaces in rgc based on the IO of a sub-GC.

    Returns:
        True if interfaces were updated, False otherwise.
    """
    if sub_gc is None:
        return False

    # Get sub-GC (might need to fetch from GPI)
    # For now, assume it's already a GCABC if it's not None
    if not isinstance(sub_gc, GCABC):
        return False

    cgraph = rgc["cgraph"]
    sub_cgraph = sub_gc["cgraph"]

    updated = False
    # Update Destination Interface (Input of sub-GC)
    if dst_key in cgraph:
        old_if = cgraph[dst_key]
        new_if = sub_cgraph[SrcIfKey.IS]
        if len(old_if) != len(new_if) or any(a.typ != b.typ for a, b in zip(old_if, new_if)):
            _logger.debug("Updating interface %s", dst_key)
            # Create new interface preserving connections where valid
            updated_if = Interface(new_if, old_if._row)
            for i, (old_ep, new_ep) in enumerate(zip(old_if, updated_if)):
                if i < len(old_if) and old_ep.is_connected():
                    # Try to preserve connection
                    ref = old_ep.refs[0]
                    # We only preserve if it's still compatible (simplified check)
                    # Real stabilization will handle full compatibility
                    new_ep.set_ref(ref.row, ref.idx)
            cgraph[dst_key] = updated_if
            updated = True

    # Update Source Interface (Output of sub-GC)
    if src_key in cgraph:
        old_if = cgraph[src_key]
        new_if = sub_cgraph[DstIfKey.OD]
        if len(old_if) != len(new_if) or any(a.typ != b.typ for a, b in zip(old_if, new_if)):
            _logger.debug("Updating interface %s", src_key)
            updated_if = Interface(new_if, old_if._row)
            # Source interfaces can have multiple connections, harder to preserve
            # For now, we clear them and let stabilization/insertion process handle it
            cgraph[src_key] = updated_if
            updated = True

    return updated


def crossover_connection_process(rgc: EGCode) -> EGCode:
    """Implement connection processing for crossover cases.

    If interfaces changed, we update them and then execute insertion process.
    """
    updated_a = update_interface_from_gc(rgc, DstIfKey.AD, SrcIfKey.AS, rgc.get("gca"))
    updated_b = update_interface_from_gc(rgc, DstIfKey.BD, SrcIfKey.BS, rgc.get("gcb"))

    if updated_a or updated_b:
        return insert_connection_process(rgc)
    return rgc
