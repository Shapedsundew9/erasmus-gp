"""References Abstract Base Class"""
from abc import ABC, abstractmethod
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ReferencesABC(ABC):
    """References Abstract Base Class.
    
    References reference endpoints in interfaces. They are defined at one end of a
    connection to refer to the other. A reference consists of a row letter and an index.
    The context in which it is used i.e. by a connection definition at a destination
    interface informs that the reference is to a source interface.
    """