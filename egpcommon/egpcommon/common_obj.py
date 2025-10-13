"""Common Object  Class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CommonObj:
    """Common Object Class.

    The Common Object Class, CommonObj, is the base class for all custom objects in EGP.
    EGP has the philosophy that all objects should be able to verify their own data and check
    their own consistency. The methods defined here shall always be called by derived classes.
    """

    __slots__ = tuple()

    def consistency(self, _result: bool = False) -> bool:
        """Check the consistency of the CommonObj.

        The consistency() method is used to check the semantic of the CommonObj
        object. An object verified by verify() may not raise an exception because each of its
        values is individually correct but may raise one in a consistency() check because of
        an invalid relationship between values that is expensive to check. Typically examples
        would involve heavy IO or complex calculations.

        The consistency() method shall raise a RuntimeError if the object is not
        consistent and the log level is CONSISTENCY or lower.
        If the log level is higher than CONSISTENCY the consistency() method shall return False
        if the object is not consistent.
        If the object is consistent the consistency() method shall return True.

        Failed checks shall be logged at the CONSISTENCY level with a message indicating
        the reason for the failure. Ideally containing the invalid value and
        the valid range of values if it can be displayed concisely.

        NOTE: Likely to significantly slow down the code.

        Args:
            _result: Internal use only. AND'd with the result of any tests in derived classes.
                Defaults to False to ensure derived class tests are run and properly pass
                results through to this base class method.

        Returns:
            bool: True if the object is consistent, False otherwise.
        """
        if _LOG_CONSISTENCY:
            _logger.log(level=CONSISTENCY, msg=f"Consistency check passed for {self}")
        return True

    def verify(self, _result: bool = False) -> bool:
        """Verify the CommonObj object.

        The verify() method is used to check the CommonObj objects data for validity.
        e.g. correct value ranges, lengths, types etc. with relatively fast checks.

        *IMPORTANT*
        The verify() method shall raise a ValueError if the object is not valid and
        the log level is VERIFY or lower.
        If the log level is higher than VERIFY the verify() method shall return False
        if the object is not valid.
        If the object is valid the verify() method shall return True.

        Failed checks shall be logged at the VERIFY level with a message indicating
        the reason for the failure. Ideally containing the invalid value and
        the valid range of values if it can be displayed concisely.

        Args:
            _result: Internal use only. AND'd with the result of any tests in derived classes.
                Defaults to False to ensure derived class tests are run and properly pass
                results through to this base class method.

        Returns:
            bool: True if the object is valid, False otherwise.
        """
        if _logger.isEnabledFor(level=CONSISTENCY) and _result:
            _logger.log(level=CONSISTENCY, msg=f"Verify check passed for {self}")
        return _result
