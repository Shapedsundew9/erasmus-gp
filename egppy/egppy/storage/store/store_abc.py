"""Store Base Abstract Base Class"""

from typing import Any, Hashable
from collections.abc import MutableMapping
from abc import abstractmethod
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.store.storable_obj_abc import StorableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StoreABC(MutableMapping):
    """Abstract class for Store base classes.
    
    The Store class must implement all the primitives of Store operations.
    """
    @abstractmethod
    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the Store."""

    @abstractmethod
    def __setitem__(self, key: Hashable, value: StorableObjABC) -> None:
        """Set an item in the Store."""

    @abstractmethod
    def setdefault(self, key: Hashable, default: StorableObjABC) -> Any:  # type: ignore pylint: disable=signature-differs
        """Set a default item in the Store."""

    @abstractmethod
    def update(  # type: ignore pylint: disable=arguments-differ
        self, m: MutableMapping[Hashable, StorableObjABC]) -> None:
        """Update the store."""

    @abstractmethod
    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("Stores do not support pop.")

    @abstractmethod
    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("Stores do not support popitem.")
