"""In Memory Store store module.
This module provides a Store that can be used for testing.
"""
from egppy.storage.store.store_abc import StoreABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.store_base import StoreBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InMemoryStore(dict, StoreBase, StoreABC):
    """An in memory store class that can be used for testing."""

    def __init__(self, flavor: type[StorableObjABC]) -> None:
        """Initialize the store."""
        dict.__init__(self)
        StoreBase.__init__(self, flavor=flavor)

    def verify(self) -> None:
        """Verify the store."""
        if not self.flavor:
            raise ValueError('Flavor not set')
        for value in self.values():
            if not isinstance(value, self.flavor):
                raise ValueError(f'Value {value} not of type {self.flavor}')
