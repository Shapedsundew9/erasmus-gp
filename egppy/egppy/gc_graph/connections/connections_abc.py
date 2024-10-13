"""Connections Abstract Base Class"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Iterable

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsABC(CommonObjABC):
    """Abstract Base Class for Genetic Code Graph Connections between Interface Endpoints.

    ConnectionsABC does not inherent from CacheableObjABC because the connections are
    stored within the graph object and are not cached separately.

    Connections are read-only once created. Modifying connections (and interfaces) is
    done by manipluating endpoints which are written to the read-only connections object
    when complete.

    Connections can be considered as a tuple-like of tuple-likes of endpoint references.
    Even if an endpoint has no connections it must be represented by an empty tuple-like.
    If an interface has no endpoints it must be represented by an empty tuple-like.
    Consequently the length of an interface is the same as the length of the connections.

    In theory connection objects can be shared between multiple graphs.

    NOTE: The __init__() method is not required for an abstract base class but may call verify()
    or otherwise assert the object is valid.
    """

    @abstractmethod
    def __init__(self, conns: Iterable[Iterable[XEndPointRefABC]] | ConnectionsABC) -> None:
        """Initialize the connections."""
        raise NotImplementedError("Connections.__init__ must be overridden")

    @abstractmethod
    def __delitem__(self, index: int) -> None:
        """Delete the connection."""
        raise NotImplementedError("Connections.__delitem__ must be overridden")

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        """Return the list of connections."""
        raise NotImplementedError("Connections.__getitem__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Any:
        """Iterate over the connections."""
        raise NotImplementedError("Connections.__iter__ must be overridden")

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of endpoints (connections).
        NOTE: An endpoint may have no connections but still be valid.
        """
        raise NotImplementedError("Connections.__len__ must be overridden")

    @abstractmethod
    def __setitem__(self, index: int, value: Any) -> None:
        """Set the connection."""
        raise NotImplementedError("Connections.__setitem__ must be overridden")

    @abstractmethod
    def append(self, value: Iterable[XEndPointRefABC]) -> None:
        """Append the connection."""
        raise NotImplementedError("Connections.append must be overridden")
