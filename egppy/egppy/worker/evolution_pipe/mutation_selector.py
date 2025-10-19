"""Mutation selector module for evolution pipeline."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.worker.evolution_pipe.mutation_queue import mutation_queue

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def mutation_selector():
    """Select a mutation to apply."""
    mutation_queue()
