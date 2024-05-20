"""Null store module.
This module provides a null store class that can be used as a placeholder.
"""
from typing import Any, Iterator
from egppy.storage.store.store_abc import StoreABC


class NullStore(StoreABC):
    """A null store class that can be used as a placeholder."""
    def __getitem__(self, key: Any) -> Any:
        """Get an item from the store."""
        return None

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an item in the store."""

    def __delitem__(self, key: Any) -> None:
        """Delete an item from the store."""

    def __contains__(self, key: Any) -> bool:
        """Check if an item is in the store."""
        return False

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the store."""
        return iter([])

    def __len__(self) -> int:
        """Get the length of the store."""
        return 0

    def clear(self) -> None:
        """Clear the store."""
