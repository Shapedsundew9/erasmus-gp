"""Common logging tools & configurations for EGP."""
from logging import Logger, NullHandler, getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL


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


_logger: Logger = egp_logger(name=__name__)
if _logger.isEnabledFor(level=CONSISTENCY):
    _logger.debug("EGP logger created and set for CONSISTENCY level logging.")
elif _logger.isEnabledFor(level=VERIFY):
    _logger.debug("EGP logger created and set for VERIFY level logging.")
elif _logger.isEnabledFor(level=DEBUG):
    _logger.debug("EGP logger created and set for DEBUG level logging.")
elif _logger.isEnabledFor(level=INFO):
    _logger.info("EGP logger created and set for INFO level logging.")
elif _logger.isEnabledFor(level=WARNING):
    _logger.warning("EGP logger created and set for WARNING level logging.")
elif _logger.isEnabledFor(level=ERROR):
    _logger.error("EGP logger created and set for ERROR level logging.")
elif _logger.isEnabledFor(level=CRITICAL):
    _logger.critical("EGP logger created and set for CRITICAL level logging.")
elif _logger.isEnabledFor(level=FATAL):
    _logger.fatal("EGP logger created and set for FATAL level logging.")
else: # pragma: no cover
    _logger.info("EGP logger created and set for NULL level logging.")
