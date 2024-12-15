"""The interfcae base class module."""

from typing import Any, Protocol

from egpcommon.common_obj_mixin import CommonObjMixin, CommonObjProtocol
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.types_def import EndPointType, types_db
from egppy.gc_graph.interface.interface_abc import InterfaceABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Interface constants
INTERFACE_MAX_LENGTH: int = 256


class InterfaceProtocol(CommonObjProtocol, Protocol):
    """Interface Protocol."""

    def __delitem__(self, index: int) -> None:
        """Delete the endpoint type."""

    def __getitem__(self, index: int) -> Any:
        """Return the endpoint type."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __len__(self) -> int:
        """Return the length of the interface."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __iter__(self) -> Any:
        """Iterate over the interface."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __setitem__(self, index: int, value: Any) -> None:
        """Set the endpoint type."""

    def find(self, typ: EndPointType) -> list[int]:
        """Return the indices of each endpoint with type typ."""
        ...  # pylint: disable=unnecessary-ellipsis


class InterfaceMixin(CommonObjMixin):
    """Interface Mixin class.

    The InterfaceBase class is a subclass of InterfaceABC.
    It is the base class for all interface objects.
    """

    def __eq__(self: InterfaceProtocol, other: object) -> bool:
        """Return True if the interfaces are equal."""
        if not isinstance(other, InterfaceABC):
            return False
        if len(self) != len(other):
            return False
        return all(x == y for x, y in zip(self, other))

    def find(self: InterfaceProtocol, typ: EndPointType) -> list[int]:
        """Return the indices of each endpoint with type typ."""
        return [idx for idx, ept in enumerate(self) if ept == typ]

    def verify(self: InterfaceProtocol) -> None:
        """Verify the interface."""
        assert len(self) <= INTERFACE_MAX_LENGTH, "Interface has too many endpoints."
        assert not self.find(types_db["egp_invalid"].ept()), "Interface has void endpoints."
        super().verify()
