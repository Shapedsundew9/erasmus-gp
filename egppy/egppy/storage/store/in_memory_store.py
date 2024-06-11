"""In Memory Store store module.
This module provides a Store that can be used for testing.
"""
from typing import Any
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_illegal import StoreIllegal
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.store_base import StoreBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InMemoryStore(StoreIllegal, dict, StoreBase, StoreABC):  # type: ignore
    """An in memory store class that can be used for testing."""

    def __init__(self, flavor: type[StorableObjABC]) -> None:
        """Initialize the store."""
        dict.__init__(self)
        StoreBase.__init__(self, flavor=flavor)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an item in the store."""
        if _LOG_DEBUG:
            _logger.debug("Setting item in InMemoryStore: %s: %s", key, value)
        return super().__setitem__(key, value)
