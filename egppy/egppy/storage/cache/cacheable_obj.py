"""Cacheable Dictionary Base Class module."""

from collections.abc import MutableMapping, MutableSequence, MutableSet, Sequence
from copy import deepcopy
from typing import Any, Iterable, Iterator

from egpcommon.common import NULL_TUPLE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_obj_mixin import CacheableObjMixin

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableDict(MutableMapping, CacheableObjMixin, CacheableObjABC):
    """Cacheable Dictionary Class.
    The CacheableDict uses a builtin dictionary for storage but wraps the __setitem__
    and update methods to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, dictlike: Any = None) -> None:
        """Initialize the CacheableDict."""
        if dictlike is not None:
            if isinstance(dictlike, dict):
                self.data: dict[str, Any] = deepcopy(dictlike)
            elif isinstance(dictlike, CacheableDict):
                self.data: dict[str, Any] = deepcopy(dictlike.data)
            else:
                self.data: dict[str, Any] = {str(k): deepcopy(v) for k, v in dictlike.items()}
        else:
            self.data: dict[str, Any] = {}
        super().__init__()

    def __contains__(self, key: object) -> bool:
        """Check if the dictionary contains a key."""
        return key in self.data

    def __delitem__(self, key: str) -> None:
        """Delete an item from the dictionary."""
        del self.data[key]
        self.dirty()

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        if isinstance(other, CacheableDict):
            return self.data == other.data
        if isinstance(other, dict):
            return self.data == other
        return False

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

    def get(self, key: Any, default: Any = None) -> Any:
        """Get an item from the dictionary."""
        self.touch()
        return self.data.get(key, default)

    def popitem(self) -> tuple[Any, Any]:
        """Default MutableMapping mixin popitem() method is implemented
        using FIFO ordering which is inconsistent with python 3.7+ dict."""
        if len(self) > 0:
            key = tuple(self.keys())[-1]
        else:
            raise KeyError from None
        value = self[key]
        del self[key]
        return key, value

    def to_json(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self.data)

    def verify(self) -> bool:
        """Verify the cacheable object."""
        non_str_keys = tuple(x for x in self if not isinstance(x, str))
        assert not non_str_keys, f"Keys must be strings: Non-string keys {non_str_keys}."
        return super().verify()


class CacheableList(MutableSequence, CacheableObjMixin, CacheableObjABC):
    """Cacheable List Class.
    The CacheableList uses a builtin list for storage but implements the MutableSequence
    interface to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, iterable: Iterable | None = None) -> None:
        """Initialize the CacheableList."""
        if iterable is not None:
            if isinstance(iterable, list):
                self.data: list = deepcopy(iterable)
            elif isinstance(iterable, CacheableList):
                self.data: list = deepcopy(iterable.data)
            else:
                self.data: list = [deepcopy(v) for v in iterable]
        else:
            self.data: list = []
        super().__init__()

    def __delitem__(self, i: int | slice) -> None:
        """Delete an item from the list."""
        del self.data[i]
        self.dirty()

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        if isinstance(other, CacheableList):
            return self.data == other.data
        if isinstance(other, Iterable):
            return self.data == [v for v in other]
        return False

    def __getitem__(self, i: int | slice) -> Any:
        """Get an item from the list."""
        _logger.debug("CacheableList.__getitem__ i: %s", str(i))
        self.touch()
        _logger.debug("CacheableList.__getitem__ data: %s", str(self.data))
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


class CacheableTuple(Sequence, CacheableObjMixin, CacheableObjABC):
    """Cacheable Tuple Class.
    Cacheable tuple objects cannot be modified so will never mark themseleves dirty.
    However, the dirty() and clean() methods are provided for consistency and can be used
    to copyback() automatically should that have someside effect that requires it.
    """

    def __init__(self, iterable: Iterable | None = None) -> None:
        """Initialize the CacheableList."""
        if iterable is not None:
            self.data: tuple = tuple(deepcopy(v) for v in iterable)
        else:
            self.data: tuple = NULL_TUPLE
        super().__init__()

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        if isinstance(other, CacheableTuple):
            return self.data == other.data
        if isinstance(other, Iterable):
            return self.data == tuple(v for v in other)
        return False

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


class CacheableSet(MutableSet, CacheableObjMixin, CacheableObjABC):
    """Cacheable Set Class.
    The CacheableSet uses a builtin set for storage but implements the MutableSet
    interface to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, iterable: Iterable | None = None) -> None:
        """Initialize the CacheableSet."""
        if iterable is not None:
            self.data: set[Any] = set(deepcopy(v) for v in iterable)
        else:
            self.data: set[Any] = set()
        super().__init__()

    def __contains__(self, item: Any) -> bool:
        """Check if the set contains an item."""
        return item in self.data

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        if isinstance(other, CacheableSet):
            return self.data == other.data
        if isinstance(other, set):
            return self.data == other
        return False

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
