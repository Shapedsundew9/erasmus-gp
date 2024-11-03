"""The Interface Abstract Base Class module."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import MutableSequence
from typing import Iterable

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.typing import EndPointType

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceABC(MutableSequence, CommonObjABC):
    """Interface Abstract Base Class.

    The Interface Abstract Base Class, InterfaceABC, is the base class for all interface objects.
    Interface objects define the properties of an interface. It is a list-like object of integers
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
