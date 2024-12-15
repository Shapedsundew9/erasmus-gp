"""The list interface module."""

from typing import Iterable

from egpcommon.common import NULL_TUPLE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.types_def import EndPointType
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.interface.interface_mixin import InterfaceMixin

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleInterface(tuple[EndPointType, ...], InterfaceMixin, InterfaceABC):  # type: ignore
    """A tuple interface object.

    The TupleInterface class is a subclass of tuple and InterfaceMixin.
    It is a tuple-like object of integers representing endpoint types.
    """

    def __init__(self, iface: Iterable[EndPointType] | InterfaceABC = NULL_TUPLE) -> None:
        """Initialize the interface."""

    def __delitem__(self, index: slice | int) -> None:
        """Delete the endpoint type."""
        raise RuntimeError("TupleInterface.__delitem__ is not supported")

    def __setitem__(self, index: slice | int, value: EndPointType | Iterable[EndPointType]) -> None:
        """Set the endpoint type."""
        raise RuntimeError("TupleInterface.__setitem__ is not supported")

    def insert(self, index: int, value: EndPointType) -> None:
        """Insert the endpoint type."""
        raise RuntimeError("TupleInterface.insert is not supported")


class ListInterface(list[EndPointType], InterfaceMixin, InterfaceABC):  # type: ignore
    """A list interface object.

    The ListInterface class is a subclass of list and InterfaceMixin.
    It is a list-like object of integers representing endpoint types.
    """

    def __init__(self, iface: Iterable[EndPointType] = NULL_TUPLE) -> None:
        """Initialize the interface."""
        super().__init__(iface)


# To be used for all empty interface references
EMPTY_INTERFACE: TupleInterface = TupleInterface()


# Efficient storage for tuple interfaces by sharing the same object
_interface_store: dict[tuple[EndPointType, ...], tuple[EndPointType, ...]] = {}


def tuple_interface(
    iface: Iterable[EndPointType] | InterfaceABC = NULL_TUPLE,
) -> tuple[EndPointType, ...]:
    """Return the shared tuple interface object."""
    interface = tuple(iface)
    return _interface_store.setdefault(interface, interface)
