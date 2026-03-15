"""Structural optimizations for genetic codes."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, SrcRow
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.mutations.common import copy_rgc

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def dead_code_elimination(rtctxt: RuntimeContext, rgc: EGCode) -> EGCode:
    """Implement Dead Code Elimination (DCE) using bottom-up reachability.

    Identifies and removes sub-GCs (gca, gcb) that do not contribute to the output.
    A sub-GC contributes to the output if its output interface (As for GCA, Bs for GCB)
    is reachable from the main output interface (Od) or alternate output (Pd)
    through the connection graph.
    """
    cgraph = rgc["cgraph"]
    
    # 1. Identify reachable source interfaces starting from outputs
    reachable_src_rows: set[SrcRow] = set()
    
    # Starting points: Od and Pd
    to_visit_dst_ifs = [DstIfKey.OD]
    if DstIfKey.PD in cgraph and cgraph[DstIfKey.PD] is not None:
        to_visit_dst_ifs.append(DstIfKey.PD)
        
    visited_dst_ifs = set(to_visit_dst_ifs)

    while to_visit_dst_ifs:
        dst_if_key = to_visit_dst_ifs.pop(0)
        dst_if = cgraph.get(dst_if_key)
        if not dst_if:
            continue
            
        for ep in dst_if:
            for ref in ep.refs:
                src_row = ref.row
                reachable_src_rows.add(src_row)
                
                # If the source row belongs to a sub-GC, we must visit its input interface
                if src_row == SrcRow.A:
                    if DstIfKey.AD not in visited_dst_ifs:
                        visited_dst_ifs.add(DstIfKey.AD)
                        to_visit_dst_ifs.append(DstIfKey.AD)
                elif src_row == SrcRow.B:
                    if DstIfKey.BD not in visited_dst_ifs:
                        visited_dst_ifs.add(DstIfKey.BD)
                        to_visit_dst_ifs.append(DstIfKey.BD)

    # 2. Check if GCA and GCB are reachable
    gca_reachable = SrcRow.A in reachable_src_rows
    gcb_reachable = SrcRow.B in reachable_src_rows
    
    # 3. If everything is reachable, return original (no optimization needed)
    if (rgc.get("gca") is None or gca_reachable) and (rgc.get("gcb") is None or gcb_reachable):
        return rgc

    # 4. Create optimized copy
    # We set unreachable sub-GCs to None. 
    # Note: We rely on stabilization/consistency to handle the dangling interfaces
    # or we can clear them here if required by standard.
    rgc_new = copy_rgc(rgc)
    
    if rgc.get("gca") is not None and not gca_reachable:
        _logger.info("DCE: Removing unreachable GCA")
        rgc_new["gca"] = None
        # Remove interfaces from CGraph to maintain consistency
        if DstIfKey.AD in rgc_new["cgraph"]:
            del rgc_new["cgraph"][DstIfKey.AD]
        if SrcIfKey.AS in rgc_new["cgraph"]:
            del rgc_new["cgraph"][SrcIfKey.AS]

    if rgc.get("gcb") is not None and not gcb_reachable:
        _logger.info("DCE: Removing unreachable GCB")
        rgc_new["gcb"] = None
        # Remove interfaces from CGraph to maintain consistency
        if DstIfKey.BD in rgc_new["cgraph"]:
            del rgc_new["cgraph"][DstIfKey.BD]
        if SrcIfKey.BS in rgc_new["cgraph"]:
            del rgc_new["cgraph"][SrcIfKey.BS]

    return rgc_new


def unused_parameter_removal(rtctxt: RuntimeContext, rgc: EGCode) -> EGCode:
    """Implement Unused Parameter Removal.

    Identifies and removes input parameters (SrcIfKey.IS endpoints) that do not
    contribute to any reachable output interface.
    """
    cgraph = rgc["cgraph"]
    
    # 1. Identify all reachable source endpoints starting from outputs
    # (We can reuse logic similar to DCE but at endpoint level)
    reachable_eps: set[tuple[SrcRow, int]] = set()
    
    to_visit_dst_ifs = [DstIfKey.OD]
    if DstIfKey.PD in rgc["cgraph"] and rgc["cgraph"][DstIfKey.PD] is not None:
        to_visit_dst_ifs.append(DstIfKey.PD)
        
    visited_dst_ifs = set(to_visit_dst_ifs)

    while to_visit_dst_ifs:
        dst_if_key = to_visit_dst_ifs.pop(0)
        dst_if = cgraph.get(dst_if_key)
        if not dst_if:
            continue
            
        for ep in dst_if:
            for ref in ep.refs:
                src_row = ref.row
                src_idx = ref.idx
                reachable_eps.add((src_row, src_idx))
                
                # If the source belongs to a sub-GC row, continue search
                if src_row == SrcRow.A:
                    if DstIfKey.AD not in visited_dst_ifs:
                        visited_dst_ifs.add(DstIfKey.AD)
                        to_visit_dst_ifs.append(DstIfKey.AD)
                elif src_row == SrcRow.B:
                    if DstIfKey.BD not in visited_dst_ifs:
                        visited_dst_ifs.add(DstIfKey.BD)
                        to_visit_dst_ifs.append(DstIfKey.BD)

    # 2. Check IS endpoints
    is_if = cgraph.get(SrcIfKey.IS)
    if not is_if:
        return rgc
        
    unreachable_indices = []
    for i in range(len(is_if)):
        if (SrcRow.I, i) not in reachable_eps:
            unreachable_indices.append(i)
            
    if not unreachable_indices:
        return rgc

    # 3. Create optimized copy and remove parameters
    _logger.info("UPR: Removing %d unused parameters", len(unreachable_indices))
    rgc_new = copy_rgc(rgc)
    
    # Remove from highest index to lowest to avoid index shifting issues 
    # (though Interface.__delitem__ handles shifting, we want to be safe)
    for idx in sorted(unreachable_indices, reverse=True):
        del rgc_new["cgraph"][SrcIfKey.IS][idx]
        
    return rgc_new
