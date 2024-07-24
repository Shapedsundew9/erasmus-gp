"""Connections class factory module."""
from typing import Iterable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_mixin import ConnectionsMixin


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleConnections(tuple, ConnectionsMixin, ConnectionsABC):
    """A tuple connections object.

    The TupleConnections class is a subclass of tuple and ConnectionsMixin.
    It is a tuple-like object of tuples of end point references.
    """
    def __init__(self, _: Iterable[Iterable[XEndPointRefABC]]) -> None:
        """Initialize the connections."""
        super().__init__()


EMPTY_CONNECTIONS: TupleConnections = TupleConnections(tuple(tuple()))
