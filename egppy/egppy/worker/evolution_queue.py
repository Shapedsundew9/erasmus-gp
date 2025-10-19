"""Evolution queue module."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.worker.evolution_pipe.evolution_pipe import evolution_pipe

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def evolution_queue():
    """Create the evolution queue."""
    evolution_pipe()
