"""Fitness queue module."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.worker.fitness_executor import fitness_executor

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def fitness_queue():
    """Create the fitness queue."""
    fitness_executor()
