"""Illegal methods for the interface module."""
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceIllegal:
    """Illegal methods for the interface module."""

    def update(self, *args, **kwargs) -> None:
        """Update the interface."""
        raise NotImplementedError("Method not supported by interface objects.")
