"""Genetic Code Abstract Base Class"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Hashable
from typing import Any

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StorableObjABC(Hashable, CommonObjABC):
    """Abstract Base Class for Storeable Object types.

    The Storeable Object Abstract Base Class, StoreableObjABC, is the base class for all storeable
    objects in EGP. Storeable objects are objects that can be stored in a StoreABC that supports its
    subclass. They are serializable to JSON and can be re-created from their JSON representation.
    As a python type they are always a subclass of Collection.

    Note that type(self)(self.to_json()) == self shall be True.
    i.e. the object should be able to be re-created from its JSON representation when
    it is passed to the constructor.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the Storeable object."""
        raise NotImplementedError("StoreableObjABC.__init__ must be overridden")

    @abstractmethod
    def to_json(self) -> dict[str, Any] | list:
        """Return a JSON serializable representation of the object.
        The returned JSON serializable object will not contain any references to data in
        this object. The return object must be serializable by json.dump().
        """
        raise NotImplementedError("StoreableObjABC.to_json must be overridden")

    @abstractmethod
    def modified(self) -> tuple[str | int, ...] | bool:
        """Return a tuple of modified fields or a boolean indicating if the object has been
        modified. Since the object is a collection, the modified method may be used by the StoreABC
        to efficiently determine which fields have been modified and only update those in the
        store. An empty tuple is the same as returning False.
        A tuple of all fields indicates that the object has been completely modified and is
        the semantic equivilent of returning True.
        NOTE: Stores are not obligated to use this information, but it is provided for efficiency.
        """
        raise NotImplementedError("StoreableObjABC.modified must be overridden")
