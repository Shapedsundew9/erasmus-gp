"""Common logging tools & configurations for EGP."""

# pylint: disable=unused-import
# Logging levels are imported from this module in other EGP modules
from logging import INFO  # type: ignore
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    WARNING,
    Logger,
    NullHandler,
    basicConfig,
    getLogger,
)

# Custom log levels
# These custom logging levels shall only be used within blocks that are wrapped with
# `if _logger.isEnabledFor(level=DEBUG)`. They are developer debug deep verification and
# validation options. The DEBUG level should be light and quick to enable unit tests to
# execute in a few 10s of seconds. Verify should not extend that time by more than a
# factor of three and consistency may take 10 or 20 times as long to execute, but perform
# much deeper debugging and consistency checking. These levels should only raise
# `egpcommon.common.debug_exceptions`.

# Verify the correctness of values and types of data. e.g. right type, range, length etc.
# Slows down execution possibly significantly where large volumes of data are involved.
VERIFY: int = 7
# Consistency checks. e.g. check that the data is consistent with itself. Significantly
# slows down execution.
CONSISTENCY: int = 5


# Standard EGP logging pattern
def egp_logger(name: str) -> Logger:
    """Create an EGP logger."""
    _logger: Logger = getLogger(name=name)
    _logger.addHandler(hdlr=NullHandler())
    return _logger


def enable_debug_logging():
    """Enable debug logging."""
    basicConfig(
        level=CONSISTENCY,
        filename="egp.log",
        filemode="w",
        format="%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(message)s",
    )


_logger: Logger = egp_logger(name=__name__)
if _logger.isEnabledFor(level=CONSISTENCY):
    _logger.debug("EGP logger created and set for CONSISTENCY level logging.")
elif _logger.isEnabledFor(level=VERIFY):
    _logger.debug("EGP logger created and set for VERIFY level logging.")
_logger.debug("EGP logger created and set for DEBUG level logging.")
_logger.info("EGP logger created and set for INFO level logging.")
_logger.warning("EGP logger created and set for WARNING level logging.")
_logger.error("EGP logger created and set for ERROR level logging.")
_logger.critical("EGP logger created and set for CRITICAL level logging.")
_logger.fatal("EGP logger created and set for FATAL level logging.")
