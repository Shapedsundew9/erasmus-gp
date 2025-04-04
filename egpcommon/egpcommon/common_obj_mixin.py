"""Common Object Mixin Class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CommonObjMixin:
    """Common Object Mixin Class.

    The Common Object Mixin Class, CommonObjMixin, is the base class for all custom objects in EGP.
    EGP has the philosophy that all objects should be able to verify their own data and check
    their own consistency. The methods defined here shall always be called by derived classes.
    """

    def consistency(self) -> None:
        """Check the consistency of the CommonObjMixin.
        The consistency() method is used to check the semantic of the CommonObjMixin
        object. An object verified by verify() may not raise an exception because each of its
        values is individually correct but may raise one in a consistency() check because of
        an invalid relationship between values.
        The consistency() method shall raise a RuntimeError if the object is not
        consistent.
        NOTE: Likely to significantly slow down the code.
        """
        if _LOG_CONSISTENCY:
            _logger.log(level=CONSISTENCY, msg=f"Consistency check passed for {self}")

    def verify(self) -> None:
        """Verify the CommonObjMixin object.
        The verify() method is used to check the CommonObjMixin objects data for validity.
        e.g. correct value ranges, lengths, types etc.
        The verify() method shall raise a ValueError if the object is not valid.
        """
        if _LOG_VERIFY:
            _logger.log(level=VERIFY, msg=f"Verify check passed for {self}")
