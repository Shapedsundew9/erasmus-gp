"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from typing import Any
from abc import abstractmethod, ABC
from collections.abc import Hashable, Collection
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StorableObjABC(ABC):
    """Abstract Base Class for Storeable Object types.
    
    The Storeable Object Abstract Base Class, StoreableObjABC, is the base class for all storeable
    objects in EGP. Storeable objects are objects that can be stored in a StoreABC.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Constructor for StoreableObjABC.
        Note that type(self)(self.to_json()) == self should be True.
        i.e. the object should be able to be re-created from its JSON representation when
        it is passed to the constructor.
        """
        raise NotImplementedError("StoreableObjABC.__init__ must be overridden")

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the StoreableObjABC.
        The consistency() method is used to check the consistency of the StoreableObjABC
        object. An object verified by verify() may not raise an exception because each of its
        values is individually correct but may raise one in a consistency() check because of
        an invalid relationship between values.
        The consistency() method should raise a RuntimeError if the object is not
        consistent.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("StoreableObjABC.consistency must be overridden")

    @abstractmethod
    def to_json(self) -> dict[str, Any] | list:
        """Return a JSON serializable representation of the object.
        The container should be a deep copy of the object's data and should
        not include any meta data. The container should be suitable for use
        with json.dump()."""
        raise NotImplementedError("StoreableObjABC.to_json must be overridden")

    @abstractmethod
    def update(  # type: ignore pylint: disable=arguments-differ
        self, m: Collection) -> None:
        """Update the storable object."""

    @abstractmethod
    def verify(self) -> None:
        """Verify the StoreableObjABC object.
        The verify() method is used to check the StoreableObjABC objects data for validity.
        e.g. correct value ranges, lengths, types etc.
        The verify() method should raise a ValueError if the object is not
        valid.
        NOTE: May significantly slow down the code if called frequently.
        """
        raise NotImplementedError("StoreableObjABC.verify must be overridden")
