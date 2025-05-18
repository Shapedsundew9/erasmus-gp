"""Connections class factory module."""

from typing import Iterable

from egpcommon.common import NULL_TUPLE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.connections.connections_abc import ConnectionsABC
from egppy.c_graph.connections.connections_mixin import ConnectionsMixin
from egppy.c_graph.end_point.end_point_abc import XEndPointRefABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ListConnections(list, ConnectionsMixin, ConnectionsABC):  # type: ignore
    """A list connections object.

    The ListConnections class is a subclass of list and ConnectionsMixin.
    It is a list-like object of lists of end point references.
    """

    def __init__(
        self, conns: Iterable[list[XEndPointRefABC]] | ConnectionsABC = NULL_TUPLE
    ) -> None:
        """Initialize the connections."""
        if _LOG_VERIFY:
            for conn in conns:
                assert isinstance(conn, list), "ListConnections must be a list of lists."
        super().__init__(conns)

    def copy(self) -> ConnectionsABC:  # type: ignore
        """Return a copy of the connections."""
        return ListConnections([epr.copy() for epr in conn] for conn in self)

    @classmethod
    def get_ref_iterable_type(cls) -> type:  # pylint: disable=arguments-differ
        """Get the reference iterable type."""
        return list


NULL_CONNECTIONS: ListConnections = ListConnections()
