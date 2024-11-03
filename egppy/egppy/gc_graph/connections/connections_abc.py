"""Connections Abstract Base Class"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import MutableSequence
from typing import Iterable

from egpcommon.common import NULL_TUPLE
from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsABC(MutableSequence, CommonObjABC):
    """Abstract Base Class for Genetic Code Graph Connections between Interface Endpoints.

    ConnectionsABC does not inherit from CacheableObjABC because the connections are
    stored within the graph object and are not cached separately.

    Connections are read-only once created. Modifying connections (and interfaces) is
    done by manipulating endpoints which are written to the read-only connections object
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
    def __init__(
        self, conns: Iterable[Iterable[XEndPointRefABC]] | ConnectionsABC = NULL_TUPLE
    ) -> None:
        """Initialize the connections."""
        raise NotImplementedError("Connections.__init__ must be overridden")

    @classmethod
    @abstractmethod
    def get_ref_iterable_type(cls) -> type:
        """Get the reference iterable type."""
        raise NotImplementedError("Connections.get_ref_iterable_type must be overridden")

    @abstractmethod
    def get_unconnected_idx(self) -> list[int]:
        """Get a list of unconnected endpoints."""
        raise NotImplementedError("Connections.get_unconnected_idx must be overridden")

    @abstractmethod
    def has_unconnected_eps(self) -> bool:
        """Check if there are any unconnected endpoints."""
        raise NotImplementedError("Connections.has_unconnected_eps must be overridden")
