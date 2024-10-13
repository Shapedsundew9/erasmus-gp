"""Store Base Abstract Base Class"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import MutableMapping

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StoreABC(MutableMapping, CommonObjABC):
    """Abstract class for Store base classes.

    The Store class must implement all the primitives of Store operations.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the Store."""
        raise NotImplementedError("StoreABC.__init__ must be overridden")
