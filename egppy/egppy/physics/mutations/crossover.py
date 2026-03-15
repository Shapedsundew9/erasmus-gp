"""The crossover module implements crossover operations for genetic codes."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.genetic_code import GCABC
from egppy.physics.mutations.common import copy_rgc, verify_graph_size
from egppy.physics.pgc_api import EGCode
from egppy.physics.processes import crossover_connection_process
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def crossover(_: RuntimeContext, rgc: EGCode, psite2: GCABC, a: bool) -> EGCode:
    """Perform crossover by replacing GCA or GCB with another GC.

    rgc is not modified; a deep copy is created and returned (FR-010).
    The connection process handles interface updates and wiring (US2).

    Arguments:
        _: The runtime context.
        rgc: The target genetic code (TGC).
        psite2: The genetic code to swap in.
        a: If True, replace GCA. If False, replace GCB.
    Returns:
        The crossover EGCode.
    """
    _logger.debug("Crossover: Replacing %s with new genetic code", "GCA" if a else "GCB")

    # Create a deep copy for atomicity (FR-010)
    rgc_new = copy_rgc(rgc)

    if a:
        rgc_new["gca"] = psite2
    else:
        rgc_new["gcb"] = psite2

    # Execute Connection Process (US2)
    _logger.debug("Crossover: Executing connection process")
    rgc_new = crossover_connection_process(rgc_new)

    # Enforce graph size limit (FR-008)
    verify_graph_size(rgc_new)

    # Defensive validation (Principle III)
    rgc_new.verify()
    rgc_new.consistency()

    return rgc_new
