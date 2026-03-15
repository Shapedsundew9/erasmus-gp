"""The split module provides splitting operations for genetic codes."""

from egpcommon.egp_log import Logger, egp_logger
from egpcommon.properties import CGraphType, PropertiesBD
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, EPCls, SrcIfKey, SrcRow
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.types_def_store import types_def_store
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.mutations.common import copy_rgc, verify_graph_size

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def split(rtctxt: RuntimeContext, rgc: EGCode, if_key: DstIfKey | SrcIfKey) -> EGCode:
    """Introduce an if-then or if-then-else conditional branching structure.

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation uses one endpoint from the specified interface as a condition
    and restructures the graph to be conditional.

    Arguments:
        rtctxt: The runtime context.
        rgc: The genetic code to modify.
        if_key: The interface key that provides the condition endpoint.
    Returns:
        The modified EGCode.
    """
    rgc_new = copy_rgc(rgc)
    cgraph = rgc_new["cgraph"]

    if if_key not in cgraph:
        raise ValueError(f"Interface {if_key} not found in CGraph.")

    iface = cgraph[if_key]
    if len(iface) < 1:
        # Need at least one endpoint to act as a condition (or feed a condition)
        return rgc_new

    # 1. Determine the new graph type
    has_gcb = rgc_new.get("gcb") is not None
    new_type = CGraphType.IF_THEN_ELSE if has_gcb else CGraphType.IF_THEN

    # 2. Update properties
    _logger.debug("Splitting GC %s: changing graph type to %s", rgc.get("signature", "unnamed"), new_type.name)
    props = PropertiesBD(rgc_new["properties"])
    props["graph_type"] = new_type
    rgc_new["properties"] = props.to_int()

    # 3. Create Row F (Condition) interface if it doesn't exist
    if DstIfKey.FD not in cgraph or cgraph[DstIfKey.FD] is None:
        _logger.debug("Splitting GC %s: creating condition interface FD", rgc.get("signature", "unnamed"))
        # Condition endpoint typically expects 'bool'
        bool_type = types_def_store["bool"]
        f_ep = EndPoint(DstRow.F, 0, EPCls.DST, bool_type, [])
        cgraph[DstIfKey.FD] = Interface([f_ep], DstRow.F)

    # 4. Connect the split interface's first endpoint to the condition if compatible
    src_ep = iface[0]
    dst_ep = cgraph[DstIfKey.FD][0]
    if not dst_ep.is_connected() and (dst_ep.can_connect(src_ep) or dst_ep.can_downcast_connect(src_ep)):
        _logger.debug("Splitting GC %s: connecting %s[0] to FD[0]", rgc.get("signature", "unnamed"), if_key)
        dst_ep.connect(src_ep)
        src_ep.connect(dst_ep)

    # 5. If IF_THEN_ELSE, ensure GCA and GCB are parallelized
    if new_type == CGraphType.IF_THEN_ELSE:
        # Create Row P (Else Output) interface if it doesn't exist
        if DstIfKey.PD not in cgraph or cgraph[DstIfKey.PD] is None:
            # P row typically mirrors O row for the GCB branch
            o_iface = cgraph[DstIfKey.OD]
            p_eps = [EndPoint(DstRow.P, i, EPCls.DST, ep.typ, []) for i, ep in enumerate(o_iface)]
            cgraph[DstIfKey.PD] = Interface(p_eps, DstRow.P)

        # Rewire: GCB should now take input from IS (primary) and output to PD
        # (Actually connection processes will handle most of this, but we can do a preliminary move)
        # Move Bs -> Od connections to Bs -> Pd
        bs_if = cgraph.get(SrcIfKey.BS)
        od_if = cgraph.get(DstIfKey.OD)
        pd_if = cgraph.get(DstIfKey.PD)
        if bs_if and od_if and pd_if:
            for bs_ep in bs_if:
                for ref in list(bs_ep.refs):
                    # Find the destination endpoint
                    # In a STANDARD graph, BS connects to OD
                    # OD is a destination, its row is 'O'
                    if ref.row == DstRow.O:
                        idx = ref.idx
                        if idx < len(pd_if):
                            _logger.debug("Splitting GC %s: re-routing BS[%d] to PD[%d]", rgc.get("signature", "unnamed"), bs_ep.idx, idx)
                            target = od_if[idx]
                            # Disconnect BS -> OD
                            target.clr_refs()
                            # Remove target from bs_ep.refs
                            for i, r in enumerate(list(bs_ep.refs)):
                                if r.row == DstRow.O and r.idx == idx:
                                    del bs_ep.refs[i]
                                    break
                            
                            # Connect BS -> PD
                            pd_if[idx].connect(bs_ep)
                            bs_ep.connect(pd_if[idx])

    # Enforce graph size limit (FR-008)
    verify_graph_size(rgc_new)

    # Defensive validation (Principle III)
    rgc_new.verify()
    rgc_new.consistency()

    return rgc_new
