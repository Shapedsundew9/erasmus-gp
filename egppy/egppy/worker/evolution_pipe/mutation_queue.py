"""Mutation Queue module for evolution pipeline."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.worker.evolution_pipe.mutation_executor import mutation_executor

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def mutation_queue() -> None:
    """Queue the mutation."""
    mutation_executor()
