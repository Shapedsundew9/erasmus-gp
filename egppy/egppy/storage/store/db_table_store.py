"""Database Table store module."""

from typing import Any, Iterator

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpdb.configuration import TableConfig
from egpdb.table import Table

from egppy.storage.store.storable_obj import StorableDict
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_base import StoreBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class DBTableStore(StoreBase, StoreABC):
    """An in memory store class that can be used for testing."""

    def __init__(self, config: TableConfig) -> None:
        """Initialize the store."""
        self.table = Table(config=config)
        StoreBase.__init__(self, flavor=StorableDict)

    def __contains__(self, key: Any) -> bool:
        """Check if an item is in the store."""
        return key in self.table

    def __delitem__(self, key: Any) -> None:
        """Delete an item in the store."""
        self.table.delete("{pk} = {value}", literals={"value": key})

    def __getitem__(self, key: Any) -> Any:
        """Get an item from the store."""
        return self.table[key]

    def __setitem__(self, key: Any, value: StorableDict) -> None:
        """Set an item in the store. NOTE this is an UPSERT operation."""
        if self.table.raw.primary_key not in value:
            value[self.table.raw.primary_key] = key
        elif _LOG_VERIFY:
            assert value[self.table.raw.primary_key] == key
        self.table[key] = value

    def __iter__(self) -> Iterator:
        """Iterate over the store."""
        return self.keys()

    def __len__(self) -> int:
        """Get the length of the store."""
        return len(self.table)

    def keys(self) -> Iterator:  # type: ignore
        """Get the keys of the store."""
        assert self.table.raw.primary_key is not None
        return (
            key[0]
            for key in self.table.select(columns=[self.table.raw.primary_key], container="tuple")
        )

    def items(self) -> Iterator:  # type: ignore
        """Get the items of the store."""
        return ((item[self.table.raw.primary_key], item) for item in self.table.select())

    def values(self) -> Iterator:  # type: ignore
        """Get the values of the store."""
        return self.table.select()
