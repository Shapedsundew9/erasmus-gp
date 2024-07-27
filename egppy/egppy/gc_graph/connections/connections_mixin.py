"""The interfcae base class module."""
from typing import Any, Protocol
from egppy.common.common_obj_mixin import CommonObjMixin, CommonObjProtocol
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.interface.interface_mixin import INTERFACE_MAX_LENGTH

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
    """Connections Mixin class."""

    def consistency(self: ConnectionsProtocol) -> None:
        """Check the consistency of the interface."""
        for ep in self:
            for ref in ep:
                ref.consistency()
            assert all(ref.is_dst() for ref in ep) or all(ref.is_src() for ref in ep), (
                f"Connections endpoint has both source and destination row references: {self}")
        super().consistency()

    def verify(self: ConnectionsProtocol) -> None:
        """Verify the connections."""
        assert len(self) <= INTERFACE_MAX_LENGTH, f"Connections has too many endpoints: {self}"
        for ep in self:
            for ref in ep:
                ref.verify()
        super().verify()
