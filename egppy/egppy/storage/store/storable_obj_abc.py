"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from typing import Any
from abc import abstractmethod
from collections.abc import Collection
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.common.common_obj_abc import CommonObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StorableObjABC(Collection, CommonObjABC):
    """Abstract Base Class for Storeable Object types.
    
    The Storeable Object Abstract Base Class, StoreableObjABC, is the base class for all storeable
    objects in EGP. Storeable objects are objects that can be stored in a StoreABC that supports its
    subclass. They are serializable to JSON and can be re-created from their JSON representation.
    As a python type they are always a subclass of Collection.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Constructor for StoreableObjABC.
        Note that type(self)(self.to_json()) == self shall be True.
        i.e. the object should be able to be re-created from its JSON representation when
        it is passed to the constructor.
        """
        raise NotImplementedError("StoreableObjABC.__init__ must be overridden")

    @abstractmethod
    def to_json(self) -> dict[str, Any] | list:
        """Return a JSON serializable representation of the object.
        The returned JSON serializable object will not contain any references to data in 
        this object. The return object must be serializable by json.dump().
        """
        raise NotImplementedError("StoreableObjABC.to_json must be overridden")

    @abstractmethod
    def modified(self) -> tuple[str | int, ...]:
        """Return a tuple of modified fields.
        Since the object is a collection, the modified method may be used by the StoreABC to
        efficiently determine which fields have been modified and only update those in the store.
        An empty tuple indicates that the object has not been modified and is the semantic
        equivilent of a no-op.
        A tuple of all fields indicates that the object has been completely modified and is
        the semantic equivilent of a copy. The StoreABC may choose to optimize this case by
        not checking for modifications and always updating all fields.
        """
        raise NotImplementedError("StoreableObjABC.modified must be overridden")

