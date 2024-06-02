"""The Interface Abstract Base Class module."""
from __future__ import annotations
from abc import abstractmethod
from collections.abc import MutableSequence
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceABC(MutableSequence):
    """Interface Abstract Base Class.

    The Interface Abstract Base Class, InterfaceABC, is the base class for all interface objects.
    Interface objects define the properties of an interface.
    It is a subclass of MutableSequence (broadly list-like) and must implement all the primitives
    as required by MutableSequence. HOWEVER, InterfaceABC stubs out the methods that are not
    supported by
    interface objects. This is because the interface objects are designed to be lightweight
    and do not support all the methods of MutableSequence (just most of them). The most notable
    missing methods are pop, popitem, and clear. In addition an InterfaceABC derived class
    reserves the right to add meta data to the interface object, for example, but not limited
    too, dirty and lock flags. These data may be visible to the user and must not be modified
    directly by the user.
    """
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Constructor for InterfaceABC"""
        raise NotImplementedError("InterfaceABC.__init__ must be overridden")

    @abstractmethod
    def __delitem__(self, key: Any) -> None:
        """Deletion must be implemented in the derived class."""
        raise NotImplementedError("InterfaceABC.__delitem__ must be overridden")

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Equality comparison must be implemented in the derived class."""
        raise NotImplementedError("InterfaceABC.__eq__ must be overridden")

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Inequality comparison must be implemented in the derived class."""
        raise NotImplementedError("InterfaceABC.__ne__ must be overridden")

    @abstractmethod
    def clear(self) -> None:
        """Clearing the InterfaceABC must be implemented in the derived class."""
        raise NotImplementedError("InterfaceABC.clear must be overridden")

    @abstractmethod
    def clean(self) -> None:
        """Mark the InterfaceABC as clean.
        clean() is the opposite of dirty(). A clean InterfaceABC has not been
        modified since it was cleaned using this method."""
        raise NotImplementedError("InterfaceABC.clean must be overridden")

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the InterfaceABC.
        The consistency() method is used to check the consistency of the InterfaceABC
        object. This method is called by the copyback() method to ensure that
        the object is in a consistent state before it is copied back if the
        log level is set to CONSISTENCY. The
        consistency() method should raise an exception if the object is not
        consistent. The consistency() method may also be called by the user
        to check the consistency of the object.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("InterfaceABC.consistency must be overridden")

    @abstractmethod
    def copyback(self) -> InterfaceABC:
        """Copy the InterfaceABC data back.
        This method exists to support caching behaviour where the InterfaceABC may be
        a local copy of a remote object. The copyback() method is used to copy
        the local data back to the remote object. There is no requirement for
        all the data to be copied back only the data that is modified or created.
        The return object must be a InterfaceABC but does not have to be the same type as
        the object that called the method. In fact in many cases this may not
        be efficient as the modified data may only be a small subset of the
        required data. The returned object *may* be a new object, a view of the
        original object, or the original object itself.
        """
        raise NotImplementedError("InterfaceABC.copyback must be overridden")

    @abstractmethod
    def dirty(self) -> None:
        """Mark the object as dirty.
        dirty() is the opposite of clean(). A dirty InterfaceABC has been modified
        since it was cleaned using the clean() method."""
        raise NotImplementedError("InterfaceABC.dirty must be overridden")

    @abstractmethod
    def is_dirty(self) -> bool:
        """Check if the object is dirty.
        Returns True if the object has been modified since it was cleaned."""
        raise NotImplementedError("InterfaceABC.is_dirty must be overridden")

    @abstractmethod
    def json_list(self) -> list[int]:
        """Return a JSON serializable list representation of the object.
        The list should be a copy of the object's data and should
        not include any meta data. The dictionary should be suitable for use
        with json.dump()."""
        raise NotImplementedError("InterfaceABC.json_list must be overridden")

    @abstractmethod
    def pop(self, index: int = 0, default: Any = None) -> Any:
        """Pop from an InterfaceABC."""
        raise NotImplementedError("InterfaceABC.pop must be overridden")

    @abstractmethod
    def verify(self) -> None:
        """Verify the InterfaceABC object.
        The verify() method is used to check the InterfaceABC object for validity.
        The verify() method should raise an exception if the object is not
        valid. The verify() method may also be called by the user to check the
        validity of the object. The verify() method is called by the copyback()
        method if the _LOG_VERIFY level is set. The verify() method should not
        be called by the user unless the user has a good reason to do so.
        NOTE: May significantly slow down the code if called frequently.
        """
        raise NotImplementedError("InterfaceABC.verify must be overridden")
