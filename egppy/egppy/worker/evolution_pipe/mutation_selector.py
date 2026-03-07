"""Mutation selector module for evolution pipeline."""

from egpcommon.codon_dev_load import find_codon_signature
from egpcommon.egp_log import Logger, egp_logger
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.genetic_code import GCABC
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.worker.evolution_pipe.mutation_queue import mutation_queue
from egppy.worker.executor.execution_context import ExecutionContext

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# The selector execution context is created once.
# TODO: This a placeholder using the local DB manager gene pool interface.
_sec = ExecutionContext(GenePoolInterface(LOCAL_DB_MANAGER_CONFIG), 50)
_sps = find_codon_signature([], ["GGCode"], "random_simple_pgc_selector")


def mutation_selector(tgc: GCABC) -> None:
    """Select a mutation to apply to tgc and queue it for execution.

    Args:
        tgc: The target genetic code to which the mutation will be applied.
    """
    pgc = _sec.execute(_sps, tuple())
    mutation_queue(pgc, tgc)
