"""The Gene Pool Interface."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpdb.configuration import DatabaseConfig

from egppy.gene_pool.gene_pool_interface_abc import GPIABC
from egppy.genetic_code.interface import Interface
from egppy.populations.configuration import PopulationConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenePoolInterface(GPIABC):
    """Gene Pool Interface.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a configuration file describing the Gene Pool database connection
    and provides methods to pull and push Genetic Codes to and from it.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize the Gene Pool Interface."""
        self.config = config.copy()

    def consistency(self) -> bool:
        """Check the consistency of the Gene Pool."""
        return True

    def initial_generation_query(self, pconfig: PopulationConfig) -> list[bytes]:
        """Query the Gene Pool for the initial generation of this population."""
        # Place holder for the actual implementation
        return []

    def select_gc(self, _: Interface) -> bytes | None:
        """Select a Genetic Code with the exact input types."""
        # Place holder for the actual implementation
        return None

    def verify(self) -> bool:
        """Verify the Gene Pool."""
        return True
