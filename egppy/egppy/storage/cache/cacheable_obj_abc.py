"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from abc import abstractmethod
from itertools import count
from collections.abc import Collection
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Universal sequence number generator
SEQUENCE_NUMBER_GENERATOR = count(start=-2**63)


class CacheableObjABC(StorableObjABC):
    """Abstract Base Class for EGP Cacheable Object Types.
    
    The Cacheable Object Abstract Base Class, CacheableObjABC, is the base class for all cacheable
    objects in EGP. Cacheable objects are objects that can be stored in a CacheABC.
    """

    @abstractmethod
    def clean(self) -> None:
        """Mark the Cacheable object as clean.
        clean() is the opposite of dirty(). A clean cacheable object has not been
        modified since it was cleaned using this method."""
        raise NotImplementedError("CacheableObjABC.clean must be overridden")

    @abstractmethod
    def copyback(self) -> Collection:
        """Copy the CacheableObjABC data back to the CacheABC next level StoreABC.
        This method exists to support caching behaviour where the object may be
        a local copy of a remote object. The copyback() method is used to copy
        the local data back to the remote object. There is no requirement for
        all the data to be copied back only the data that is modified or created.
        The return object must be a subclass of CacheableObjABC but does not have
        to be the same type as the object that called the method. In fact in many 
        cases this may not be efficient as the modified data may only be a small
        subset of the required data. The returned object *may* be a new object, a
        view of the original object, or the original object itself.
        """
        raise NotImplementedError("CacheableObjABC.copyback must be overridden")

    @abstractmethod
    def dirty(self) -> None:
        """Mark the object as dirty.
        dirty() is the opposite of clean(). A dirty CacheableObjABC has been modified
        since it was cleaned using the clean() method."""
        raise NotImplementedError("CacheableObjABC.dirty must be overridden")

    @abstractmethod
    def is_dirty(self) -> bool:
        """Check if the object is dirty.
        Returns True if the object has been modified since it was cleaned."""
        raise NotImplementedError("CacheableObjABC.is_dirty must be overridden")

    @abstractmethod
    def seq_num(self) -> int:
        """Get the access sequence number.
        The access sequence number is used to determine the least recently used
        items for purging. The sequence number is updated when
        the object is accessed."""
        raise NotImplementedError("CacheableObjABC.seq_num must be overridden")

    @abstractmethod
    def touch(self) -> None:
        """Touch the cache item to update the access sequence number.
        Touching an item updates the access sequence number to the current
        value of the access counter. This is used to determine the least
        recently used items for purging.
        """
        raise NotImplementedError("touch must be overridden")
