"""Store Base class module."""
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.common.common_obj_base import CommonObjBase
from egppy.common.common_obj_abc import CommonObjABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StoreBase(CommonObjBase, CommonObjABC):
    """Store Base class has methods generic to all store classes."""

    def __init__(self, flavor: type[StorableObjABC]) -> None:
        """All stores must have a flavor."""
        self.flavor: type[StorableObjABC] = flavor
        CommonObjBase.__init__(self)
