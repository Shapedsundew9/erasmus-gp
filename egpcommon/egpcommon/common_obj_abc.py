"""Common Object Abstract Base Class"""

from abc import ABC, abstractmethod

from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class CommonObjABC(ABC):
    """Abstract Base Class for Common Object types.

    See CommonObj for details.
    """

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the CommonObjABC."""
        raise NotImplementedError("CommonObjABC.consistency must be overridden")

    @abstractmethod
    def verify(self) -> None:
        """Verify the CommonObjABC object."""
        raise NotImplementedError("CommonObjABC.verify must be overridden")
