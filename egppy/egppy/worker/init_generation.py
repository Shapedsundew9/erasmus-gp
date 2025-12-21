"""Create the initial generation of individuals."""

from typing import Any

from egpcommon.egp_log import Logger, egp_logger
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.populations.configuration import PopulationConfig
from egppy.worker.configuration import WorkerConfig
from egppy.worker.evolution_queue import evolution_queue
from egppy.worker.fitness_queue import fitness_queue

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def best_igp(pconfig: PopulationConfig, gene_pool: GenePoolInterface) -> list[Any]:
    """Return a list of GC's meeting the BEST criteria for the population."""
    igp = []
    _logger.debug(
        "BEST initial generation search returned %d results for '%s' population",
        len(igp),
        pconfig.name,
    )
    return igp


def diverse_igp(pconfig: PopulationConfig, gene_pool: GenePoolInterface) -> list[Any]:
    """Return a list of GC's meeting the DIVERSE criteria for the population."""
    igp = []
    _logger.debug(
        "DIVERSE initial generation search returned %d results for '%s' population",
        len(igp),
        pconfig.name,
    )
    _logger.debug("D")
    return igp


def init_generation(config: WorkerConfig) -> None:
    """Initialize the generation."""

    # Connect to the Gene Pool and find the best phenotypes
    gene_pool = GenePoolInterface(config.databases[config.gene_pool])

    # Initial Generation Population list
    # List per population.
    # Population lists of valid GC's meeting population interface definition and
    # a valid fitness score (0.0 to 1.0 inclusive)
    igp_list = [[] for _ in config.populations.configs]
    for pconfig, igp in zip(config.populations.configs, igp_list, strict=True):
        size = sum(
            (
                pconfig.best_source.limit,
                pconfig.diverse_source.limit,
                pconfig.related_source.limit,
                pconfig.unrelated_source.limit,
                pconfig.spontaneous_source.limit,
            )
        )
        # TODO: Make the number of times we do this configurable in the population configuration
        for _ in range(2):
            # Add GC's for each type of initial generation
            igp.extend(best_igp(pconfig, gene_pool))
            igp.extend(diverse_igp(pconfig, gene_pool))
            igp.extend(related_igp(pconfig, gene_pool))
            igp.extend(unrelated_igp(pconfig, gene_pool))
            igp.extend(spontaneous_igp(pconfig, gene_pool))
            if len(igp) >= size:
                assert len(igp) <= size, "Initial generation size exceeded limit!"
                _logger.info(
                    "Initial '%s' generation size: %d of maximum %d", pconfig.name, len(igp), size
                )
                break

    # If the population is not full, fill it with new individuals
    # The new individuals are created from a stabilized empty genetic code meeting
    # the population interface requirements.
    # for igp, pconfig in zip(igps, config.populations.configs, strict=True):
    #    igp.extend([new_gc(pconfig, gene_pool) for _ in range(pconfig.size - len(igp))])
    evolution_queue()
    fitness_queue()


def related_igp(pconfig: PopulationConfig, gene_pool: GenePoolInterface) -> list[Any]:
    """Return a list of GC's meeting the RELATED criteria for the population."""
    igp = []
    _logger.debug(
        "RELATED initial generation search returned %d results for '%s' population",
        len(igp),
        pconfig.name,
    )
    _logger.debug("D")
    return igp


def spontaneous_igp(pconfig: PopulationConfig, gene_pool: GenePoolInterface) -> list[Any]:
    """Return a list of GC's meeting the SPONTANEOUS criteria for the population."""
    igp = []
    _logger.debug(
        "SPONTANEOUS initial generation search returned %d results for '%s' population",
        len(igp),
        pconfig.name,
    )
    _logger.debug("D")
    return igp


def unrelated_igp(pconfig: PopulationConfig, gene_pool: GenePoolInterface) -> list[Any]:
    """Return a list of GC's meeting the UNRELATED criteria for the population."""
    igp = []
    _logger.debug(
        "UNRELATED initial generation search returned %d results for '%s' population",
        len(igp),
        pconfig.name,
    )
    _logger.debug("D")
    return igp
