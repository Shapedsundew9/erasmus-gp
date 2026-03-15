"""The DCE module provides dead code elimination operations for genetic codes."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.optimization import dead_code_elimination
from egppy.physics.mutations.common import verify_graph_size

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def dce(rtctxt: RuntimeContext, rgc: EGCode) -> EGCode:
    """Perform Dead Code Elimination on the genetic code.

    rgc is not modified; if dead code is found, a deep copy is created,
    optimized, and returned. Otherwise, the original rgc is returned.

    Arguments:
        rtctxt: The runtime context.
        rgc: The genetic code to optimize.
    Returns:
        The optimized EGCode.
    """
    _logger.debug("DCE: Starting dead code elimination")
    rgc_new = dead_code_elimination(rtctxt, rgc)
    
    if rgc_new is not rgc:
        # Enforce graph size limit (though DCE should only reduce size)
        verify_graph_size(rgc_new)
        
        # Defensive validation
        rgc_new.verify()
        rgc_new.consistency()
        _logger.debug("DCE: Optimization complete")

    return rgc_new
