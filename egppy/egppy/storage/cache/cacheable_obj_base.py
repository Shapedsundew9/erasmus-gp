"""Cacheable object base class."""
from itertools import count
from egppy.storage.store.storable_obj_base import StorableObjBase
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Universal sequence number generator
SEQUENCE_NUMBER_GENERATOR = count(start=-2**63)


class CacheableObjBase(StorableObjBase):
    """Cacheable object base class aka high priority MRO mixin."""
