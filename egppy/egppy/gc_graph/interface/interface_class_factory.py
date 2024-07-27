"""The list interface module."""
from typing import Iterable
from egppy.gc_graph.interface.interface_mixin import InterfaceMixin
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.egp_typing import EndPointType
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleInterface(tuple[EndPointType, ...], InterfaceMixin, InterfaceABC):
    """A tuple interface object.

    The TupleInterface class is a subclass of tuple and InterfaceMixin.
    It is a tuple-like object of integers representing endpoint types.
    """
    def __init__(self, iface: Iterable[EndPointType] | InterfaceABC) -> None:
        """Initialize the interface."""

    def __delitem__(self, index: int) -> None:
        """Delete the endpoint type."""
        raise RuntimeError("TupleInterface.__delitem__ is not supported")

    def __setitem__(self, index: int, value: EndPointType) -> None:
        """Set the endpoint type."""
        raise RuntimeError("TupleInterface.__setitem__ is not supported")

    def append(self, value: EndPointType) -> None:
        """Append the endpoint type."""
        raise RuntimeError("TupleInterface.append is not supported")


class ListInterface(list[EndPointType], InterfaceMixin, InterfaceABC):  #type: ignore
    """A list interface object.

    The ListInterface class is a subclass of list and InterfaceMixin.
    It is a list-like object of integers representing endpoint types.
    """
    def __init__(self, iface: Iterable[EndPointType]) -> None:
        """Initialize the interface."""
        super().__init__(iface)


# To be used for all empty interface references
EMPTY_INTERFACE: TupleInterface = TupleInterface(tuple())
