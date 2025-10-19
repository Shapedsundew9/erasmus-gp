"""Database Table store module."""

from typing import Any, Iterator

from egpcommon.egp_log import Logger, egp_logger
from egpdb.configuration import TableConfig
from egpdb.table import Table
from egppy.storage.store.storable_obj import StorableDict
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_base import StoreBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class DBTableStore(StoreBase, StoreABC):
    """An in memory store class that can be used for testing."""

    def __init__(self, config: TableConfig, flavor: type = StorableDict) -> None:
        """Initialize the store."""
        self.table = Table(config=config)
        pk: None | str = self.table.raw.primary_key
        if pk is None:
            raise ValueError("Table must have a primary key")
        self._pk = pk
        self._columns = tuple(col for col in self.table.raw.columns if col != self._pk)
        StoreBase.__init__(self, flavor=flavor)

    def __contains__(self, key: Any) -> bool:
        """Check if an item is in the store."""
        return key in self.table

    def __delitem__(self, key: Any) -> None:
        """Delete an item in the store."""
        self.table.delete(f"{self._pk}" + " = {_value_}", literals={"_value_": key})

    def __getitem__(self, key: Any) -> Any:
        """Get an item from the store."""
        retval = tuple(
            self.table.select(
                f"WHERE {self._pk}" + " = {_key_}",
                literals={"_key_": key},
            )
        )
        if len(retval) != 1:
            raise KeyError(f"{len(retval)} keys found key = '{key}'")
        return self.flavor(retval[0])

    def __setitem__(self, key: Any, value: StorableObjABC) -> None:
        """Set an item in the store. NOTE this is an UPSERT operation."""
        self.table[key] = value  # .to_json()

    def __iter__(self) -> Iterator:
        """Iterate over the store."""
        return self.keys()

    def __len__(self) -> int:
        """Get the length of the store."""
        return len(self.table)

    def keys(self) -> Iterator:  # type: ignore
        """Get the keys of the store."""
        assert self.table.raw.primary_key is not None
        return (key[0] for key in self.table.select(columns=[self._pk], container="tuple"))

    def items(self) -> Iterator:  # type: ignore
        """Get the items of the store."""
        return (
            (
                item[self.table.raw.primary_key],
                item,
            )
            for item in self.table.select()
        )

    def values(self) -> Iterator:  # type: ignore
        """Get the values of the store."""
        return self.table.select()
