"""The iterate module provides iteration (loop) operations for genetic codes."""

from egpcommon.properties import CGraphType, PropertiesBD
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.mutations.common import copy_rgc, verify_graph_size


def iterate(rtctxt: RuntimeContext, rgc: EGCode, loop_type: CGraphType) -> EGCode:
    """Convert a standard GC into a loop GC (FOR or WHILE).

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation changes the graph type and sets up loop-specific interfaces.

    Arguments:
        rtctxt: The runtime context.
        rgc: The genetic code to modify.
        loop_type: The type of loop (CGraphType.FOR_LOOP or CGraphType.WHILE_LOOP).
    Returns:
        The modified EGCode.
    """
    if loop_type not in [CGraphType.FOR_LOOP, CGraphType.WHILE_LOOP]:
        raise ValueError("loop_type must be FOR_LOOP or WHILE_LOOP")

    rgc_new = copy_rgc(rgc)
    # Wrap properties in PropertiesBD to make it editable (as it may be an int)
    props = PropertiesBD(rgc_new["properties"])
    props["graph_type"] = loop_type
    rgc_new["properties"] = props.to_int()

    # TODO: Setup loop-specific interfaces (Sd, Ss, Td, etc.)
    # This involves adding interfaces to the CGraph based on loop type rules.

    # Enforce graph size limit (FR-008)
    verify_graph_size(rgc_new)

    # Defensive validation
    rgc_new.verify()
    rgc_new.consistency()

    return rgc_new
