"""The interface base class module."""

from egpcommon.common_obj_mixin import CommonObjMixin
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.connections.connections_abc import ConnectionsABC
from egppy.c_graph.interface import INTERFACE_MAX_LENGTH
from egppy.c_graph.c_graph_constants import Row

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsMixin(CommonObjMixin):
    """
    Connections Mixin class.

    This mixin provides methods to check the consistency and verify the connections
    of an interface. It ensures that all connections are either source or destination
    references and that the number of connections does not exceed the maximum allowed length.
    """

    def __eq__(self, other: object) -> bool:
        """Return True if the connections are equal."""
        assert isinstance(self, ConnectionsABC), f"Invalid type: {type(self)}"
        if not isinstance(other, ConnectionsABC):
            return False
        if len(self) != len(other):
            return False
        for x, y in zip(self, other, strict=True):
            if len(x) != len(y) or not all(a == b for a, b in zip(x, y, strict=True)):
                return False
        return True

    def consistency(self) -> None:
        """Check the consistency of the interface."""
        assert isinstance(self, ConnectionsABC), f"Invalid type: {type(self)}"
        for ep in self:
            for ref in ep:
                ref.consistency()
            assert all(ref.is_dst() for ref in ep) or all(
                ref.is_src() for ref in ep
            ), f"Connections endpoint {ep} has both source and destination row references: {self}"
        super().consistency()

    def get_unconnected_idx(self) -> list[int]:
        """Return a list of unconnected endpoints."""
        assert isinstance(self, ConnectionsABC), f"Invalid type: {type(self)}"
        return [idx for idx, ep in enumerate(self) if len(ep) == 0]

    def has_unconnected_eps(self) -> bool:
        """Check if any of the connections are unconnected."""
        assert isinstance(self, ConnectionsABC), f"Invalid type: {type(self)}"
        if len(self) == 0:
            # No endpoints to be unconnected
            return False
        return any(len(ep) == 0 for ep in self)

    def row_in(self, row: Row) -> bool:
        """Check if a row is in the connections."""
        assert isinstance(self, ConnectionsABC), f"Invalid type: {type(self)}"
        for ep in self:
            if row in ep:
                return True
        return False

    def verify(self) -> None:
        """Verify the connections."""
        assert isinstance(self, ConnectionsABC), f"Invalid type: {type(self)}"
        assert (
            len(self) <= INTERFACE_MAX_LENGTH
        ), f"Connections has too many endpoints: {len(self)} (max {INTERFACE_MAX_LENGTH}): {self}"
        for ep in self:
            for ref in ep:
                ref.verify()
        super().verify()
