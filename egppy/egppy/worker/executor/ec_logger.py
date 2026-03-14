"""Execution Context Logger

This module creates an execution environment and providers helper functions
to log the structure of GC's for debugging purposes. These operations are
potentially expensive and should be used with OBJECT or TRACE logging levels.
"""

from egpcommon.egp_log import FATAL, Logger, egp_logger
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.physics.pgc_api import GGCode
from egppy.worker.executor.execution_context import ExecutionContext
from egppy.worker.executor.gc_node import GCNode

# Logging setup
_logger: Logger = egp_logger(name=__name__)


# Global execution context for logging purposes.
# Lazily defined as it is expensive to create and may not be needed in all contexts.
_ecl: dict[GenePoolInterface, ExecutionContext] = {}


def get_ec(gpi: GenePoolInterface):
    """Get the global execution context, creating it if it does not exist."""
    if gpi not in _ecl:
        _logger.debug("Creating global execution logging context for GPI %s.", gpi.uuid)
        _ecl[gpi] = ExecutionContext(gpi, 32767)
    return _ecl[gpi]


def gc_mermaid_cg(gpi: GenePoolInterface, gc: GGCode) -> str:
    """Generate a Mermaid graph definition for the connection graph of a GC."""
    # Set logging level to FATAL to avoid excessive logging from the
    # execution context during graph generation.
    log_level = _logger.level
    _logger.setLevel(FATAL)

    if not isinstance(gc, GGCode):
        raise TypeError(f"Expected GGCode, got {type(gc)}.")
    ec = get_ec(gpi)
    ng = ec.node_graph(gc)
    ng.line_count(ec.line_limit())
    ntw: list[GCNode] = ec.create_code_graphs(ng)
    chartstr = ""
    for node in ntw:
        chartstr += "\n```mermaid\n" + node.code_mermaid_chart() + "\n```\n"

    # Restore original logging level.
    _logger.setLevel(log_level)
    return chartstr
