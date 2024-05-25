"""Store Base Abstract Base Class"""

from typing import Any
from collections.abc import MutableMapping
from abc import abstractmethod
from egppy.gc_types.gc_abc import GCABC
from egppy.gc_types.null_gc import NULL_GC


class StoreABC(MutableMapping):
    """Abstract class for Store base classes.
    
    The Store class must implement all the primitives of Store operations.
    """
    @abstractmethod
    def __getitem__(self, key: Any) -> GCABC:
        """Get an item from the Store."""

    @abstractmethod
    def __setitem__(self, key: Any, value: GCABC) -> None:
        """Set an item in the Store."""

    @abstractmethod
    def setdefault(self, key: Any, default: GCABC = NULL_GC) -> GCABC:  # type: ignore
        """Set a default item in the Store."""

    @abstractmethod
    def update(  # type: ignore pylint: disable=arguments-differ
        self, m: MutableMapping[Any, GCABC]) -> None:
        """Update the store."""

    @abstractmethod
    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("Stores do not support pop.")

    @abstractmethod
    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("Stores do not support popitem.")
