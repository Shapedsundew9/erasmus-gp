"""The delete module provides deletion operations for genetic codes."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.mutations.common import copy_rgc, verify_graph_size

# Logging setup
_logger: Logger = egp_logger(name=__name__)


from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, SRC_KEY_DICT, DST_KEY_DICT


def delete(rtctxt: RuntimeContext, rgc: EGCode, a: bool = False, b: bool = False) -> EGCode:
    """Delete GCA (if a is True) and/or GCB (if b is True).

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation removes the sub-GC and clears related interface connections.

    Arguments:
        rtctxt: The runtime context.
        rgc: The genetic code to modify.
        a: If True, delete GCA.
        b: If True, delete GCB.
    Returns:
        The modified EGCode.
    """
    rgc_new = copy_rgc(rgc)
    cgraph = rgc_new["cgraph"]

    if a:
        _logger.debug("Deleting GCA from GC %s", rgc.get("signature", "unnamed"))
        rgc_new["gca"] = None
        # Clear connections for Ad and As
        for if_key in [DstIfKey.AD, SrcIfKey.AS]:
            if if_key in cgraph and cgraph[if_key] is not None:
                for ep in cgraph[if_key]:
                    for ref in list(ep.refs):
                        # Find the other side
                        other_if_key = (
                            SRC_KEY_DICT[ref.row] if ep.cls == EPCls.DST else DST_KEY_DICT[ref.row]
                        )
                        other_if = cgraph[other_if_key]
                        if other_if:
                            other = other_if[ref.idx]
                            # Remove ep from other.refs
                            for i, r in enumerate(list(other.refs)):
                                if r.row == ep.row and r.idx == ep.idx:
                                    del other.refs[i]
                                    break
                    ep.clr_refs()
                # Remove interface from CGraph to maintain consistency with gca=None
                del cgraph[if_key]

    if b:
        _logger.debug("Deleting GCB from GC %s", rgc.get("signature", "unnamed"))
        rgc_new["gcb"] = None
        # Clear connections for Bd and Bs
        for if_key in [DstIfKey.BD, SrcIfKey.BS]:
            if if_key in cgraph and cgraph[if_key] is not None:
                for ep in cgraph[if_key]:
                    for ref in list(ep.refs):
                        # Find the other side
                        other_if_key = (
                            SRC_KEY_DICT[ref.row] if ep.cls == EPCls.DST else DST_KEY_DICT[ref.row]
                        )
                        other_if = cgraph[other_if_key]
                        if other_if:
                            other = other_if[ref.idx]
                            # Remove ep from other.refs
                            for i, r in enumerate(list(other.refs)):
                                if r.row == ep.row and r.idx == ep.idx:
                                    del other.refs[i]
                                    break
                    ep.clr_refs()
                # Remove interface from CGraph to maintain consistency with gcb=None
                del cgraph[if_key]

    # Enforce graph size limit (FR-008)
    verify_graph_size(rgc_new)

    # Defensive validation (Principle III)
    rgc_new.verify()
    rgc_new.consistency()

    return rgc_new
