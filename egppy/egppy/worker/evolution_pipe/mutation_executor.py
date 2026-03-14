"""Mutation executor module."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.egc_dict import EGCDict
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.stabilization import stabilize_gc
from egppy.worker.executor.execution_context import ExecutionContext
from egppy.worker.fitness_queue import fitness_queue

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# The mutation execution context is created once.
# TODO: This a placeholder using the local DB manager gene pool interface.
_mec = ExecutionContext(GenePoolInterface(LOCAL_DB_MANAGER_CONFIG), 50)


def mutation_executor(pgc: GGCDict, tgc: GCABC) -> None:
    """Execute the mutation."""
    outputs = _mec.execute(pgc, (tgc,))
    for egc in (e for e in outputs if isinstance(e, EGCDict)):
        fitness_queue(stabilize_gc(RuntimeContext(_mec.gpi), egc))
