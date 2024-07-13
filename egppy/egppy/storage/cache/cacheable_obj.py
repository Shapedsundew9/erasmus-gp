"""Cacheable Dictionary Base Class module."""
from typing import Any, Iterator, Protocol
from copy import deepcopy
from collections.abc import MutableMapping, MutableSequence, Sequence, MutableSet
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_obj_base import CacheableObjBase, SEQUENCE_NUMBER_GENERATOR



# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableObjMixinProtocol(Protocol):
    """Cacheable Mixin Protocol Class.
    Used to add cacheable functionality to a class.
    """

    def clean(self) -> None:
        """Mark the object as clean."""

    def dirty(self) -> None:
        """Mark the object as dirty."""

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        ...  # pylint: disable=unnecessary-ellipsis

    def seq_num(self) -> int:
        """Dirty dicts do not track sequence numbers."""
        ...  # pylint: disable=unnecessary-ellipsis

    def touch(self) -> None:
        """Dirty dict objects cannot be touched."""


class CacheableObjMixin():
    """Cacheable Mixin Class.
    Used to add cacheable functionality to a class.
    """

    def __init__(self) -> None:
        """Constructor."""
        self._dirty: bool = True
        # deepcode ignore unguarded~next~call: Cannot raise StopIteration
        self._seq_num: int = next(SEQUENCE_NUMBER_GENERATOR)

    def clean(self) -> None:
        """Mark the object as clean."""
        self._dirty = False

    def dirty(self) -> None:
        """Mark the object as dirty."""
        self._dirty = True
        self.touch()

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self._dirty

    def seq_num(self) -> int:
        """Dirty dicts do not track sequence numbers."""
        return self._seq_num

    def touch(self) -> None:
        """Dirty dict objects cannot be touched."""
        # deepcode ignore unguarded~next~call: Cannot raise StopIteration
        self._seq_num: int = next(SEQUENCE_NUMBER_GENERATOR)


class CacheableDict(CacheableObjBase, MutableMapping, CacheableObjMixin, CacheableObjABC):
    """Cacheable Dictionary  Class.
    The CacheableDict uses a builtin dictionary for storage but wraps the __setitem__
    and update methods to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the CacheableDict."""
        self.data: dict[str, Any] = dict(*args, **kwargs)
        super().__init__()

    def __delitem__(self, key: str) -> None:
        """Delete an item from the dictionary."""
        del self.data[key]
        self.dirty()

    def __getitem__(self, key: Any) -> Any:
        """Get an item from the dictionary."""
        self.touch()
        return self.data[key]

    def __iter__(self) -> Iterator[str]:
        """Return an iterator for the dictionary."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return the number of items in the dictionary."""
        return len(self.data)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item in the dictionary."""
        self.data[key] = value
        self.dirty()

    def to_json(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self.data)

    def verify(self) -> None:
        """Verify the genetic code object."""
        assert not (x for x in self if not isinstance(x, str)), "Keys must be strings."
        super().verify()


class CacheableList(CacheableObjBase, MutableSequence, CacheableObjMixin, CacheableObjABC):
    """Cacheable List Class.
    The CacheableList uses a builtin list for storage but implements the MutableSequence
    interface to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, *args) -> None:
        """Initialize the CacheableList."""
        self.data: list[Any] = list(*args)
        super().__init__()

    def __delitem__(self, i: int | slice) -> None:
        """Delete an item from the list."""
        del self.data[i]
        self.dirty()

    def __getitem__(self, i: int | slice) -> Any:
        """Get an item from the list."""
        self.touch()
        return self.data[i]

    def __len__(self) -> int:
        """Return the number of items in the list."""
        return len(self.data)

    def __setitem__(self, i: int | slice, value: Any) -> None:
        """Set an item in the list."""
        self.data[i] = value
        self.dirty()

    def insert(self, index: int, value: Any) -> None:
        """Insert an item in the list."""
        self.data.insert(index, value)
        self.dirty()

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self.data)


class CacheableTuple(CacheableObjBase, Sequence, CacheableObjMixin, CacheableObjABC):
    """Cacheable Tuple Class.
    Cacheable tuple objects cannot be modified so will never mark themseleves dirty.
    However, the dirty() and clean() methods are provided for consistency and can be used
    to copyback() automatically should that have someside effect that requires it.
    """

    def __init__(self, *args) -> None:
        """Initialize the CacheableList."""
        self.data: tuple = tuple(*args)
        super().__init__()

    def __getitem__(self, i: int | slice) -> Any:
        """Get an item from the list."""
        self.touch()
        return self.data[i]

    def __len__(self) -> int:
        """Return the number of items in the list."""
        return len(self.data)

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return list(deepcopy(self.data))


class CacheableSet(CacheableObjBase, MutableSet, CacheableObjMixin, CacheableObjABC):
    """Cacheable Set Class.
    The CacheableSet uses a builtin set for storage but implements the MutableSet
    interface to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, *args) -> None:
        """Initialize the CacheableSet."""
        self.data: set[Any] = set(*args)
        super().__init__()

    def __contains__(self, item: Any) -> bool:
        """Check if the set contains an item."""
        return item in self.data

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator for the set."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return the number of items in the set."""
        return len(self.data)

    def add(self, value: Any) -> None:
        """Add an item to the set."""
        self.data.add(value)
        self.dirty()

    def discard(self, value: Any) -> None:
        """Discard an item from the set."""
        self.data.discard(value)
        self.dirty()

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return list(deepcopy(self.data))
