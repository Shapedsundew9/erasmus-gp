"""Null store module.
This module provides a null store class that can be used as a placeholder.
"""
from typing import Any, Iterator
from collections.abc import Hashable
from collections.abc import MutableMapping
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


class NullStore(StoreIllegal, StoreBase, StoreABC):
    """A null store class that can be used as a placeholder."""

    def __contains__(self, key: Hashable) -> bool:  # type: ignore
        """Check if an item is in the store."""
        return False

    def __delitem__(self, key: Hashable) -> None:
        """Delete an item from the store."""

    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the store."""
        return None

    def __iter__(self) -> Iterator:
        """Iterate over the store."""
        return iter([])

    def __len__(self) -> int:
        """Get the length of the store."""
        return 0

    def __setitem__(self, key: Hashable, value: StorableObjABC) -> None:
        """Set an item in the store."""

    def clear(self) -> None:
        """Clear the store."""

    def consistency(self) -> None:
        """Check the consistency of the store."""

    def setdefault(self, key: Hashable, default: StorableObjABC) -> Any:
        """Set a default item in the store."""
        return default

    def update(self, m: MutableMapping[Hashable, StorableObjABC]) -> None:
        """Update the store."""

    def verify(self) -> None:
        """Verify the store."""
