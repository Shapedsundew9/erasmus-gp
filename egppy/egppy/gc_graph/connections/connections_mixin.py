"""The interface base class module."""

from typing import Any, Protocol

from egpcommon.common_obj_mixin import CommonObjMixin, CommonObjProtocol
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.interface import INTERFACE_MAX_LENGTH

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsProtocol(CommonObjProtocol, Protocol):
    """Connections Protocol class."""

    def __delitem__(self, index: int) -> None:
        """Delete the connection."""

    def __getitem__(self, index: int) -> Any:
        """Return the list of connections."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __iter__(self) -> Any:
        """Iterate over the connections."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __len__(self) -> int:
        """Return the length of the interface / connections."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __setitem__(self, index: int, value: Any) -> None:
        """Set the connection."""


class ConnectionsMixin(CommonObjMixin):
    """
    Connections Mixin class.

    This mixin provides methods to check the consistency and verify the connections
    of an interface. It ensures that all connections are either source or destination
    references and that the number of connections does not exceed the maximum allowed length.
    """

    def __eq__(self: ConnectionsProtocol, other: object) -> bool:
        """Return True if the connections are equal."""
        if not isinstance(other, ConnectionsABC):
            return False
        if len(self) != len(other):
            return False
        for x, y in zip(self, other, strict=True):
            if len(x) != len(y) or not all(a == b for a, b in zip(x, y, strict=True)):
                return False
        return True

    def consistency(self: ConnectionsProtocol) -> None:
        """Check the consistency of the interface."""
        for ep in self:
            for ref in ep:
                ref.consistency()
            assert all(ref.is_dst() for ref in ep) or all(
                ref.is_src() for ref in ep
            ), f"Connections endpoint {ep} has both source and destination row references: {self}"
        super().consistency()

    def get_unconnected_idx(self: ConnectionsProtocol) -> list[int]:
        """Return a list of unconnected endpoints."""
        return [idx for idx, ep in enumerate(self) if len(ep) == 0]

    def has_unconnected_eps(self: ConnectionsProtocol) -> bool:
        """Check if any of the connections are unconnected."""
        if len(self) == 0:
            # No endpoints to be unconnected
            return False
        return any(len(ep) == 0 for ep in self)

    def verify(self: ConnectionsProtocol) -> None:
        """Verify the connections."""
        assert (
            len(self) <= INTERFACE_MAX_LENGTH
        ), f"Connections has too many endpoints: {len(self)} (max {INTERFACE_MAX_LENGTH}): {self}"
        for ep in self:
            for ref in ep:
                ref.verify()
        super().verify()
