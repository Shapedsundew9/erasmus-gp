"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from typing import Any
from collections.abc import MutableMapping
from abc import abstractmethod
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


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
    def __init__(self, *args, **kwargs) -> None:
        """Constructor for GCABC"""
        raise NotImplementedError("GCABC.__init__ must be overridden")

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
        raise AssertionError("GC's do not support __delitem__.")

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Equality comparison must be implemented in the derived class."""
        raise NotImplementedError("GCABC.__eq__ must be overridden")

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Inequality comparison must be implemented in the derived class."""
        raise NotImplementedError("GCABC.__ne__ must be overridden")

    def clear(self) -> None:
        """Clearing the mapping is not supported because GCABC have protected
        key:value pairs that should not be deleted."""
        raise AssertionError("GC's do not support clear()")

    @abstractmethod
    def clean(self) -> None:
        """Mark the GCABC as clean.
        clean() is the opposite of dirty(). A clean GCABC has not been
        modified since it was cleaned using this method."""
        raise NotImplementedError("GCABC.clean must be overridden")

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the GCABC.
        The consistency() method is used to check the consistency of the GCABC
        object. This method is called by the copyback() method to ensure that
        the object is in a consistent state before it is copied back if the
        log level is set to CONSISTENCY. The
        consistency() method should raise an exception if the object is not
        consistent. The consistency() method may also be called by the user
        to check the consistency of the object.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("GCABC.consistency must be overridden")

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
        raise NotImplementedError("GCABC.copyback must be overridden")

    @abstractmethod
    def dirty(self) -> None:
        """Mark the object as dirty.
        dirty() is the opposite of clean(). A dirty GCABC has been modified
        since it was cleaned using the clean() method."""
        raise NotImplementedError("GCABC.dirty must be overridden")

    @abstractmethod
    def is_dirty(self) -> bool:
        """Check if the object is dirty.
        Returns True if the object has been modified since it was cleaned."""
        raise NotImplementedError("GCABC.is_dirty must be overridden")

    @abstractmethod
    def json_dict(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary representation of the object.
        The dictionary should be a deep copy of the object's data and should
        not include any meta data. The dictionary should be suitable for use
        with json.dump()."""
        raise NotImplementedError("GCABC.json_dict must be overridden")

    def pop(self, key: Any, default: Any = None) -> Any:
        """Popping from a GCABC is not supported. A GCABC is not an ordered
        container and some items cannot be removed so popping an item is prohibited."""
        raise AssertionError("GC's do not support pop().")

    def popitem(self) -> tuple:
        """Popping from a GCABC is not supported. A GCABC is not an ordered
        container and some items cannot be removed so popping an item is prohibited."""
        raise AssertionError("GC's do not support popitem().")

    @abstractmethod
    def verify(self) -> None:
        """Verify the GCABC object.
        The verify() method is used to check the GCABC object for validity.
        The verify() method should raise an exception if the object is not
        valid. The verify() method may also be called by the user to check the
        validity of the object. The verify() method is called by the copyback()
        method if the _LOG_VERIFY level is set. The verify() method should not
        be called by the user unless the user has a good reason to do so.
        NOTE: May significantly slow down the code if called frequently.
        """
        raise NotImplementedError("GCABC.verify must be overridden")
