"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from typing import Any
from logging import Logger, NullHandler, getLogger, DEBUG
from collections.abc import MutableMapping
from abc import abstractmethod


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


class GCABC(MutableMapping):
    """Abstract Base Class for Genetic Code Types.
    
    The Genetic Code Abstract Base Class, GCABC, is the base class for all genetic code objects.
    It is a subclass of MutableMapping (broadly dict-like) and must implement all the primitives
    as required by MutableMapping. HOWEVER, GCABC stubs out the methods that are not supported by
    Genetic Code objects. This is because the Genetic Code objects are designed to be lightweight
    and do not support all the methods of MutableMapping (just most of them). The most notable
    missing methods are pop, popitem, and clear. In addition a GCABC derived class
    reserves the right to add meta data to the genetic code object, for example, but not limited
    too, dirty and lock flags. These data may be visible to the user and must not be modified
    directly by the user.
    """

    @abstractmethod
    def __delitem__(self, key: Any) -> None:
        """Deleting an item from a GCABC object is restricted.
        Some key:value pairs may be immutable or have special meaning.
        The __delitem__ implementation should check the protected keys and
        raise an AssertionError if the key is protected.
        Since __delitem__ cannot be used to delete a key:value pair that is
        protected it is not required to set the dirty flag. Anything that
        can be deleted would not be copied back.
        """

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Equality comparison must be implemented in the derived class."""

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Inequality comparison must be implemented in the derived class."""

    def clear(self) -> None:
        """Clearing the mapping is not supported because GCABC have protected
        key:value pairs that should not be deleted."""
        raise AssertionError("GC's do not support clear()")

    @abstractmethod
    def clean(self) -> None:
        """Mark the GCABC as clean.
        clean() is the opposite of dirty(). A clean GCABC has not been
        modified since it was cleaned using this method."""

    @abstractmethod
    def copyback(self) -> GCABC:
        """Copy the GCABC data back.
        This method exists to support caching behaviour where the GCABC may be
        a local copy of a remote object. The copyback() method is used to copy
        the local data back to the remote object. There is no requirement for
        all the data to be copied back only the data that is modified or created.
        The return object must be a GCABC but does not have to be the same type as
        the object that called the method. In fact in many cases this may not
        be efficient as the modified data may only be a small subset of the
        required data. The returned object *may* be a new object, a view of the
        original object, or the original object itself.
        """

    @abstractmethod
    def dirty(self) -> None:
        """Mark the object as dirty.
        dirty() is the opposite of clean(). A dirty GCABC has been modified
        since it was cleaned using the clean() method."""

    @abstractmethod
    def is_dirty(self) -> bool:
        """Check if the object is dirty.
        Returns True if the object has been modified since it was cleaned."""

    @abstractmethod
    def json_dict(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary representation of the object.
        The dictionary should be a deep copy of the object's data and should
        not include any meta data. The dictionary should be suitable for use
        with json.dump()."""

    def pop(self, key: Any, default: Any = None) -> Any:
        """Popping from a GCABC is not supported. A GCABC is not an ordered
        container and some items cannot be removed so popping an item is prohibited."""
        raise AssertionError("GC's do not support pop().")

    def popitem(self) -> tuple:
        """Popping from a GCABC is not supported. A GCABC is not an ordered
        container and some items cannot be removed so popping an item is prohibited."""
        raise AssertionError("GC's do not support popitem().")
