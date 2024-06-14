"""The interfcae base class module."""
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.ep_type import validate

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Interface constants
INTERFACE_MAX_LENGTH: int = 256


class InterfaceBase():
    """Interface Base class.

    The InterfaceBase class is a subclass of InterfaceABC.
    It is the base class for all interface objects.
    """

    def __len__(self) -> int:
        """Return the length of the interface."""
        raise NotImplementedError("Must be implemented by subclass.")

    def __iter__(self) -> Any:
        """Iterate over the interface."""
        raise NotImplementedError("Must be implemented by subclass.")

    def consistency(self) -> None:
        """Check the consistency of the interface."""

    def verify(self) -> None:
        """Verify the interface."""
        _logger.info("Verifying the interface.")
        assert len(self) <= INTERFACE_MAX_LENGTH, "Interface has too many endpoints."
        for ept in self:
            assert validate(ept), f"Endpoint type is invalid = {ept}"
