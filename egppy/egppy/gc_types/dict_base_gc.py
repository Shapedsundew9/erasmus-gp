"""Dictionary Genetic Code Base Class module."""
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dict import CacheableDict
from egppy.gc_types.gc_abc import GCABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class DictBaseGC(CacheableDict, GCABC):
    """Dictionary Genetic Code Base Class.
    The DictBaseGC uses a builtin dictionary for storage but wraps the __setitem__
    and update methods to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """
