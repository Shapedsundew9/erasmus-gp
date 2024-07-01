"""The Interface Abstract Base Class module."""
from __future__ import annotations
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.egp_typing import EndPointType


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceABC():
    """Interface Abstract Base Class.

    The Interface Abstract Base Class, InterfaceABC, is the base class for all interface objects.
    Interface objects define the properties of an interface. It is a tuple-like object of integers
    representing endpoint types.

    Interfaces and connections are closely related but archiecturally distinct to allow storage
    optimisation.
    """

    def __getitem__(self, index: int) -> EndPointType:
        """Return the endpoint type."""
        raise NotImplementedError("Interface.__getitem__ must be overridden")

    def __iter__(self) -> Any:
        """Iterate over the endpoints."""
        raise NotImplementedError("Interface.__iter__ must be overridden")

    def __len__(self) -> int:
        """Return the number of endpoints."""
        raise NotImplementedError("Interface.__len__ must be overridden")

    def consistency(self) -> None:
        """Check the consistency of the Interface."""
        raise NotImplementedError("Interface.consistency must be overridden")

    def verify(self) -> None:
        """Verify the Interface object."""
        raise NotImplementedError("Interface.verify must be overridden")
