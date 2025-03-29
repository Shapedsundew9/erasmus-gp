"""Common logging tools & configurations for EGP."""

# pylint: disable=unused-import
# Logging levels are imported from this module in other EGP modules
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,  # type: ignore
    WARNING,
    Logger,
    NullHandler,
    getLogger,
    basicConfig,
)

# Custom log levels
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
    basicConfig(level=DEBUG, filename="egp.log", filemode="w",
        format="%(asctime)s:%(filename)s:%(lineno)d:%(levelname)s:%(message)s")


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
