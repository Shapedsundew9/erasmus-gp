"""The create module provides functions for creating new genetic codes from
EMPTY GCs (those with an EMPTY CGraph)"""

from egpcommon.egp_log import Logger, egp_logger
from egpcommon.properties import CGraphType, PropertiesBD
from egppy.physics.mutations.common import copy_rgc, verify_graph_size
from egppy.physics.pgc_api import EGCode
from egppy.physics.processes import create_connection_process
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def create(_: RuntimeContext, empty_gc: EGCode) -> EGCode:
    """Create a new GC from an empty GC.

    rgc is not modified; a deep copy is created and returned (FR-010).
    The mutation verifies interface type compatibility and structural integrity.

    Arguments:
        _: The runtime context.
        empty_gc: The empty genetic code to populate.
    Returns:
        The new EGCode.
    """
    props = PropertiesBD(empty_gc["properties"])
    assert props["graph_type"] == CGraphType.EMPTY, "Input GC must be empty to create a new GC."

    # Create a deep copy for atomicity (FR-010)
    rgc_new = copy_rgc(empty_gc)

    # If it was empty, we now want it to be standard (if it has sub-GCs)
    if rgc_new.get("gca") is not None:
        _logger.debug("Create: Converting EMPTY GC to STANDARD")
        new_props = PropertiesBD(rgc_new["properties"])
        new_props["graph_type"] = CGraphType.STANDARD
        rgc_new["properties"] = new_props.to_int()

    # Execute Connection Process (US2)
    _logger.debug("Create: Executing connection process")
    rgc_new = create_connection_process(rgc_new)

    # Enforce graph size limit (FR-008)
    verify_graph_size(rgc_new)

    # Defensive validation (Principle III)
    rgc_new.verify()
    rgc_new.consistency()

    return rgc_new
