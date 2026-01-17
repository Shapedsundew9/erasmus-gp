"""Common logging & integrity verification tools for EGP.

The logging levels defined here are used throughout EGP modules. Please
import them from this module rather than from `logging` directly to ensure
consistency. Make a note of the intended use of the custom logging levels
defined here in the comments below.

This module additionally defines integrity levels for use in data verification.
Note that the integrity levels do not allow security to be turned off. The integrity
of data outside of the trusted domain must always be verified. Integrity levels
only control the depth and extent of verification performed with the aim of catching
bugs in EGP itself early in the runtime to make issues easier to find and fix.
"""

# pylint: disable=unused-import
# Logging levels are imported from this module in other EGP modules
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    WARNING,
    Logger,
    NullHandler,
    addLevelName,
    basicConfig,
    getLogger,
)
from tkinter import OFF

from numpy import add

# Custom log levels

# Flow-level logging.
# e.g. DB lifecycling, Gene Pool lifecycling, overall simulation progress etc.
FLOW: int = 15
addLevelName(FLOW, "FLOW")

# Genetic code load/store, selection logging.
GC_DEBUG: int = DEBUG
addLevelName(GC_DEBUG, "GC_DEBUG")

# Object's below GC level (that make up GC's) level logging.
OBJECT: int = 7
addLevelName(OBJECT, "OBJECT")

# Very detailed tracing, e.g. entry and exit of functions/methods with parameters and return values.
TRACE: int = 4
addLevelName(TRACE, "TRACE")


# Integrity verification


class Integrity:
    """Integrity verification levels for EGP data.
    Verify the correctness of values and types of data. e.g. right type, range, length etc.
    Slows down execution possibly significantly where large volumes of data are involved.

    VERIFY: int = 20
        Verify the correctness of values and types of data. e.g. right type, range, length etc.
        Slows down execution moderately.
    CONSISTENCY: int = 10
        Verify the structural consistency of data. e.g. cross references, graph integrity etc.
        Slows down execution possibly significantly where large volumes of data are involved.
    DISABLED: int = 0
        Disable integrity verification.
    """

    VERIFY: int = 20
    CONSISTENCY: int = 10
    DISABLED: int = 0
    _level: int = DISABLED

    @classmethod
    def set_level(cls, level: int):
        """Set the integrity verification level."""
        cls._level = level

    @classmethod
    def get_level(cls) -> int:
        """Get the integrity verification level."""
        return cls._level

    @classmethod
    def is_enabled_for(cls, level: int) -> bool:
        """Check if the given integrity level is enabled."""
        return cls._level >= level


# Standard EGP logging pattern
def egp_logger(name: str) -> Logger:
    """Create an EGP logger."""
    _logger: Logger = getLogger(name=name)
    _logger.addHandler(hdlr=NullHandler())
    return _logger
