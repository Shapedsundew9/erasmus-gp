"""Genetic Code Abstract Base Class"""

from __future__ import annotations

from abc import abstractmethod

from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.store.storable_obj_abc import StorableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


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
    def dirty(self) -> None:
        """Mark the object as dirty.
        dirty() is the opposite of clean(). A dirty CacheableObjABC has been modified
        since it was cleaned using the clean() method. Dirtying an object also touches
        it (see touch())"""
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
