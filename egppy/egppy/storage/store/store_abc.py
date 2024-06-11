"""Store Base Abstract Base Class"""

from typing import Any
from collections.abc import Collection, MutableMapping, Hashable
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
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the Store."""

    @abstractmethod
    def __contains__(self, key: object) -> bool:
        """Check if an item is in the Store."""

    @abstractmethod
    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the Store."""

    @abstractmethod
    def __setitem__(self, key: Hashable, value: StorableObjABC) -> None:
        """Set an item in the Store."""

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the StoreABC.
        The consistency() method is used to check the consistency of the StoreABC
        object. An object verified by verify() may not raise an exception because each of its
        values is individually correct but may raise one in a consistency() check because of
        an invalid relationship between values.
        The consistency() method should raise a RuntimeError if the object is not
        consistent.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("StoreABC.consistency must be overridden")

    @abstractmethod
    def setdefault(self, key: Hashable, default: StorableObjABC) -> Any:  # type: ignore pylint: disable=signature-differs
        """Set a default item in the Store."""

    @abstractmethod
    def update(  # type: ignore pylint: disable=arguments-differ
        self, m: MutableMapping[Hashable, StorableObjABC]) -> None:
        """Update the store."""

    @abstractmethod
    def update_value(self, key: Hashable, value: Collection) -> None:
        """Update the value of an item in the store. This is a more efficient
        version of the __setitem__ method that only updates the value of an
        existing item in the store where it needs updating.
        """

    @abstractmethod
    def verify(self) -> None:
        """Verify the StoreABC object.
        The verify() method is used to check the StoreABC objects data for validity.
        e.g. correct value ranges, lengths, types etc.
        The verify() method should raise a ValueError if the object is not
        valid.
        NOTE: May significantly slow down the code if called frequently.
        """
        raise NotImplementedError("StoreABC.verify must be overridden")
