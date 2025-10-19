"""Mutation executor module."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.worker.fitness_queue import fitness_queue

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def mutation_executor():
    """Execute the mutation."""
    fitness_queue()
