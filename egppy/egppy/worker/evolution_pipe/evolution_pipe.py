"""Define an evolution pipeline."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.worker.evolution_pipe.mutation_selector import mutation_selector

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def evolution_pipe():
    """Create the evolution pipeline."""
    mutation_selector()
