"""The create module provides functions for creating new genetic codes from
EMPTY GCs (those with an EMPTY CGraph)"""

from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext


def create(rtctxt: RuntimeContext, empty_gc: EGCode) -> EGCode:
    """Create a new GC from an empty GC. The new GC is modified in place and returned."""
    assert empty_gc.is_empty(), "Input GC must be empty to create a new GC."

    # TODO: Implement creation logic. For now, we just return the empty GC as is.
    return _create_connection_process(_rgc := empty_gc)


def _create_connection_process(rgc: EGCode) -> EGCode:
    """TODO: Implement connection processing for create cases.
    rgc is modified in place and is returned."""
    return rgc
