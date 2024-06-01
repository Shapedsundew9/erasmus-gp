"""Initialize the worker.

The configuration for the worker can come from either the command line as a configuration file or,
if none is specified, from the JSON REST API. The worker will then initialize the generation and
start the work loop.
"""
from egppy.worker.init_generation import init_generation
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def init_worker():
    """Initialize the worker."""
    init_generation()


if __name__ == '__main__':
    init_worker()
