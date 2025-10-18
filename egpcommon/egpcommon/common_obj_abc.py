"""Common Object Abstract Base Class"""

from abc import ABC, abstractmethod

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CommonObjABC(ABC):
    """Abstract Base Class for Common Object types.

    See CommonObj for details.
    """

    @abstractmethod
    def consistency(self) -> bool:
        """Check the consistency of the CommonObjABC."""
        raise NotImplementedError("CommonObjABC.consistency must be overridden")

    @abstractmethod
    def verify(self) -> bool:
        """Verify the CommonObjABC object."""
        raise NotImplementedError("CommonObjABC.verify must be overridden")
