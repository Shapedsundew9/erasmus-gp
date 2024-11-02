"""Connections class factory module."""

from typing import Iterable

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_mixin import ConnectionsMixin, ConnectionsProtocol
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleConnections(tuple, ConnectionsMixin, ConnectionsProtocol, ConnectionsABC):
    """A tuple connections object.

    The TupleConnections class is a subclass of tuple and ConnectionsMixin.
    It is a tuple-like object of tuples of end point references.
    """

    def __init__(self, conns: Iterable[Iterable[XEndPointRefABC]] | ConnectionsABC) -> None:
        """Initialize the connections."""

    def __delitem__(self, _) -> None:
        """Deletion of endpoint types is not supported for TupleConnections."""
        raise RuntimeError("TupleConnections.__delitem__ is not supported")

    def __setitem__(self, _index: int, _value: Iterable[XEndPointRefABC]) -> None:
        """Setting an item is not supported for TupleConnections."""
        raise RuntimeError("TupleConnections.__setitem__ is not supported")

    def append(self, value) -> None:
        """Appending endpoint types is not supported for TupleConnections."""
        raise RuntimeError("TupleConnections.append is not supported")


class ListConnections(list, ConnectionsMixin, ConnectionsABC):  # type: ignore
    """A list connections object.

    The ListConnections class is a subclass of list and ConnectionsMixin.
    It is a list-like object of lists of end point references.
    """

    def __init__(self, conns: Iterable[Iterable[XEndPointRefABC]] | ConnectionsABC) -> None:
        """Initialize the connections."""
        super().__init__(conns)


EMPTY_CONNECTIONS: TupleConnections = TupleConnections(tuple(tuple()))
