"""Store Base class module."""
from collections.abc import Hashable, Collection, MutableSequence
from egppy.storage.store.storable_obj_abc import StorableObjABC


class StoreBase():
    """Store Base class has methods generic to all store classes."""

    def __init__(self, flavor: type[StorableObjABC]) -> None:
        """All stores must have a flavor."""
        self.flavor: type[StorableObjABC] = flavor

    def __contains__(self, key: Hashable) -> bool:
        """Check if an item is in the store."""
        raise NotImplementedError

    def __getitem__(self, key: Hashable) -> StorableObjABC:
        """Get an item from the store."""
        raise NotImplementedError

    def __setitem__(self, key: Hashable, value: StorableObjABC) -> None:
        """Set an item in the store."""
        raise NotImplementedError

    def consistency(self) -> None:
        """Check the consistency of the store."""

    def update_value(self, key: Hashable, value: Collection) -> None:
        """Update a value in the store."""
        if key in self:
            item = self[key]
            if issubclass(type(value), (list, MutableSequence)):
                self[key] = self.flavor(value)
            else:
                item.update(value)
                self[key] = item
        else:
            self[key] = self.flavor(value)

    def verify(self) -> None:
        """Verify the store."""
