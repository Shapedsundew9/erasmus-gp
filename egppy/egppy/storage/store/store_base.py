"""Store Base class module."""

from egpcommon.common_obj import CommonObj
from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egppy.storage.store.storable_obj_abc import StorableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StoreBase(CommonObj, CommonObjABC):
    """Store Base class has methods generic to all store classes."""

    def __init__(self, flavor: type[StorableObjABC]) -> None:
        """All stores must have a flavor."""
        self.flavor: type[StorableObjABC] = flavor
