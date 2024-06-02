"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from typing import Any
from collections.abc import MutableMapping
from abc import abstractmethod
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCABC(MutableMapping, CacheableObjABC):
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
        raise NotImplementedError("GCABC.__delitem__ must be overridden")

    def clear(self) -> None:
        """Clearing the mapping is not supported because GCABC have protected
        key:value pairs that should not be deleted."""
        raise AssertionError("GC's do not support clear()")

    def pop(self, key: Any, default: Any = None) -> Any:
        """Popping from a GCABC is not supported. A GCABC is not an ordered
        container and some items cannot be removed so popping an item is prohibited."""
        raise AssertionError("GC's do not support pop().")

    def popitem(self) -> tuple:
        """Popping from a GCABC is not supported. A GCABC is not an ordered
        container and some items cannot be removed so popping an item is prohibited."""
        raise AssertionError("GC's do not support popitem().")
