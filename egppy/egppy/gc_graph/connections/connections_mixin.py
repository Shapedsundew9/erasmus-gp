"""The interfcae base class module."""
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.interface.interface_mixin import INTERFACE_MAX_LENGTH

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsMixin():
    """Connections Mixin class."""

    def __len__(self) -> int:
        """Return the length of the interface / connections."""
        raise NotImplementedError("Must be implemented by subclass.")

    def consistency(self) -> None:
        """Check the consistency of the interface."""

    def verify(self) -> None:
        """Verify the connections."""
        _logger.info("Verifying connections.")
        assert len(self) <= INTERFACE_MAX_LENGTH, "Connections has too many endpoints."
