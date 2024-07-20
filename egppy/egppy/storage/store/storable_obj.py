"""Storable Dictionary Base Class module."""
from typing import Any
from copy import deepcopy
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.store.storable_obj_base import StorableObjBase
from egppy.storage.store.storable_obj_abc import StorableObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StorableDict(dict, StorableObjBase, StorableObjABC):
    """Storable Dictionary  Class.
    The StorableDict uses a builtin dictionary for storage but wraps the __setitem__
    and update methods to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def to_json(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self)


class StorableList(list, StorableObjBase, StorableObjABC):
    """Storable List Class.
    The StorableList uses a builtin list for storage but implements the MutableSequence
    interface to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self)


class StorableTuple(tuple, StorableObjBase, StorableObjABC):
    """Storable Tuple Class.
    Storable tuple objects cannot be modified so will never mark themseleves dirty.
    However, the dirty() and clean() methods are provided for consistency and can be used
    to copyback() automatically should that have someside effect that requires it.
    """

    def __init__(self, *args, **kwargs) -> None:
        """A Tuple cannot be modified after __new__ but __init__ is required by the ABC."""

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return list(deepcopy(self))


class StorableSet(set, StorableObjBase, StorableObjABC):
    """Storable Set Class.
    The StorableSet uses a builtin set for storage but implements the MutableSet
    interface to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return list(deepcopy(self))
