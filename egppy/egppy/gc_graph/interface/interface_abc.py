"""The Interface Abstract Base Class module."""
from __future__ import annotations
from typing import Any, Iterable
from abc import abstractmethod
from egppy.common.common_obj_abc import CommonObjABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.egp_typing import EndPointType


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceABC(CommonObjABC):
    """Interface Abstract Base Class.

    The Interface Abstract Base Class, InterfaceABC, is the base class for all interface objects.
    Interface objects define the properties of an interface. It is a tuple-like object of integers
    representing endpoint types.

    Interfaces and connections are closely related but archiecturally distinct to allow storage
    optimisation.

    NOTE: The __init__() method is not required for an abstract base class but may call verify()
    or otherwise assert the object is valid.
    """
    @abstractmethod
    def __init__(self, iface: Iterable[EndPointType] | InterfaceABC) -> None:
        """Initialize the interface."""
        raise NotImplementedError("Interface.__init__ must be overridden")

    @abstractmethod
    def __delitem__(self, index: int) -> None:
        """Delete the endpoint type."""
        raise NotImplementedError("Interface.__delitem__ must be overridden")

    @abstractmethod
    def __getitem__(self, index: int) -> EndPointType:
        """Return the endpoint type."""
        raise NotImplementedError("Interface.__getitem__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Any:
        """Iterate over the endpoints."""
        raise NotImplementedError("Interface.__iter__ must be overridden")

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of endpoints."""
        raise NotImplementedError("Interface.__len__ must be overridden")

    @abstractmethod
    def __setitem__(self, index: int, value: EndPointType) -> None:
        """Set the endpoint type."""
        raise NotImplementedError("Interface.__setitem__ must be overridden")

    @abstractmethod
    def append(self, value: EndPointType) -> None:
        """Append the endpoint type."""
        raise NotImplementedError("Interface.append must be overridden")
