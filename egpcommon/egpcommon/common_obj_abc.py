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

    The Common Object Abstract Base Class, CommonObjABC, is the base class for all
    custom objects in EGP. EGP has the philosophy that all objects should be able to
    verify their own data and check their own consistency. This is enforced by the
    CommonObjABC class.
    """

    @abstractmethod
    def consistency(self) -> bool:
        """Check the consistency of the CommonObjABC.
        The consistency() method is used to check the semantic of the CommonObjABC
        object. An object verified by verify() may not raise an exception because each of its
        values is individually correct but may raise one in a consistency() check because of
        an invalid relationship between values.
        The consistency() method should raise a RuntimeError if the object is not
        consistent.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("CommonObjABC.consistency must be overridden")

    @abstractmethod
    def verify(self) -> bool:
        """Verify the CommonObjABC object.
        The verify() method is used to check the CommonObjABC objects data for validity.
        e.g. correct value ranges, lengths, types etc.

        *IMPORTANT*
        """
        raise NotImplementedError("CommonObjABC.verify must be overridden")
