"""The runtime context for PGC's in a execution context."""

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.genetic_code import GCABC


class RuntimeContext:
    """PGC's require knowledge about where to look up GC's and why they were run in
    order to correctly build GC's and report fitness. This class encapsulates that
    context information for use by PGC's during execution.
    """

    def __init__(self, gpi: GenePoolInterface, parent_pgc: GCABC) -> None:
        """Initialize the runtime context.

        Args
        ----
        gpi -- the gene pool interface
        parent_pgc -- the parent (top level) PGC that is being executed
        """
        self.gpi: GenePoolInterface = gpi
        self.parent_pgc: GCABC = parent_pgc
