"""Mutation Queue module for evolution pipeline."""

from egpcommon.egp_log import Logger, egp_logger
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.worker.evolution_pipe.mutation_executor import mutation_executor

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def mutation_queue(pgc: GGCDict, tgc: GCABC) -> None:
    """Queue the mutation."""
    mutation_executor(pgc, tgc)
