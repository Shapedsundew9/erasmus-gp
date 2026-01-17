"""Common Object  Class."""

from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class CommonObj:
    """Common Object Class.

    The Common Object Class, CommonObj, is the base class for all custom objects in EGP.
    EGP has the philosophy that all objects should be able to verify their own data and check
    their own consistency. The methods defined here shall always be called by derived classes.

    Derived classes shall validate their data on input to the class (via init or setters). If
    a parameter is derived from a CommonObj derived class then it shall be verified by calling
    its verify() method.
    """

    __slots__ = tuple()

    def consistency(self):
        """Check the consistency of the CommonObj.

        The consistency() method is used to check the semantic of the CommonObj
        object. An object verified by verify() may not raise an exception because each of its
        values is individually correct but may raise one in a consistency() check because of
        an invalid relationship between values that is expensive to check. Typically examples
        would involve heavy IO or complex calculations.

        The consistency() method shall raise an exception if the object is not
        consistent. The exception message shall
        indicate the reason for the failure. Ideally containing the invalid value and
        the valid range of values if it can be displayed concisely.

        Derived classes shall override this method to add their own checks but
        shall always call the base class consistency() method at the *end* of their own
        consistency() method. This is to ensure that the consistency() method is only called
        once all other checks have passed.

        Note that the consistency() method is likely to significantly slow down the code.
        """

    def verify(self):
        """Verify the CommonObj object.

        The verify() method is used to check the CommonObj objects data for validity.
        e.g. correct value ranges, lengths, types etc. with relatively fast checks.

        *IMPORTANT*
        The verify() method shall raise an exception if the object is not valid at the
        first check that fails (for performance reasons). The exception message shall
        indicate the reason for the failure. Ideally containing the invalid value and
        the valid range of values if it can be displayed concisely.

        Derived classes shall override this method to add their own checks but
        shall always call the base class verify() method at the *end* of their own
        verify() method.
        """
