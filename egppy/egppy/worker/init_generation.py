"""Create the initial generation of individuals."""
from egppy.worker.evolution_queue import evolution_queue
from egppy.worker.fitness_queue import fitness_queue
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def init_generation():
    evolution_queue()
    fitness_queue()
