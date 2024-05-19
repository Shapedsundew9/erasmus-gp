"""Store Base Abstract Base Class"""

from typing import Any
from collections.abc import MutableMapping
from abc import abstractmethod
from egppy.gc_types.gc_abc import GCABC


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
