"""The runtime context for PGC's in a execution context."""

from typing import Any
from uuid import UUID

from egpcommon.common import ANONYMOUS_CREATOR
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_class_factory import NULL_GC


class RuntimeContext:
    """PGC's require knowledge about where to look up GC's and why they were run in
    order to correctly build GC's and report fitness. This class encapsulates that
    context information for use by PGC's during execution.
    """

    __slots__ = ("gpi", "parent_pgc", "creator", "debug_data")

    def __init__(
        self,
        gpi: GenePoolInterface,
        parent_pgc: GCABC = NULL_GC,
        creator: UUID = ANONYMOUS_CREATOR,
        debug_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the runtime context.

        Args
        ----
        gpi -- the gene pool interface
        parent_pgc -- the parent (top level) PGC that is being executed
        creator -- the UUID of the creator of the execution context
        debug_data -- a dictionary for storing debug information. Only used in
                      development and testing to store intermediate results.
                      None if not used.
        """
        self.gpi: GenePoolInterface = gpi
        self.parent_pgc: GCABC = parent_pgc
        self.creator: UUID = creator
        self.debug_data: dict[str, Any] | None = debug_data
