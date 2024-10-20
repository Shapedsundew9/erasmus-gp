"""Create the initial generation of individuals."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.worker.configuration import WorkerConfig
from egppy.worker.evolution_queue import evolution_queue
from egppy.worker.fitness_queue import fitness_queue

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def init_generation(config: WorkerConfig) -> None:
    """Initialize the generation."""

    # Connect to the Gene Pool and find the best phenotypes
    gene_pool = GenePoolInterface(config.databases[config.gene_pool])
    for pconfig in config.populations.configs:
        

    # If the population is not full, fill it with new individuals
    # The new individuals are created from a stabilized empty genetic code meeting
    # the population interface requirements.
    for igp, pconfig in zip(igps, config.populations.configs):
        igp.extend([new_gc(pconfig, gene_pool) for _ in range(pconfig.size - len(igp))])
    evolution_queue()
    fitness_queue()
