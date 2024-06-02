"""The interfcae base class module."""
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


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
        _logger.info("Checking the consistency of the interface.")

    def verify(self) -> None:
        """Verify the interface."""
        _logger.info("Verifying the interface.")
        assert len(self) <= 256, "Interface has too many endpoints."
        for ept in self:
            assert ept >= -2**16 and ept < 2**16, "Endpoint type out of range in interface."
