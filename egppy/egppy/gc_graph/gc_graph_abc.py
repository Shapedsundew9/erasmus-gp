"""Abstract base class for GC graph objects."""
from __future__ import annotations
from abc import abstractmethod
from typing import Iterable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.egp_typing import EndPointType


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCGraphABC(CacheableObjABC):
    """Abstract Base Class for Genetic Code Graphs.
    
    The graph abstract base class, GCGraphABC, is the base class for all genetic code graph objects.
    GC graph objects define connections between interfaces.

    A row is a tuple of interfaces. The row is indexed by a letter.
    An interface is indexed by the row letter and 's' or 'd' for source or destination.
    Connections are indexed by the row letter and 's' or 'd' for source or destination.
    """

    @abstractmethod
    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        raise NotImplementedError("GCGraphABC.conditional_graph must be overridden")

    @abstractmethod
    def get_connections(self, key: str) -> ConnectionsABC:
        """Return the connections object for the given key"""
        raise NotImplementedError("GCGraphABC.get_connections must be overridden")

    @abstractmethod
    def get_interface(self, key: str) -> InterfaceABC:
        """Return the interface object for the given key"""
        raise NotImplementedError("GCGraphABC.get_interface must be overridden")

    @abstractmethod
    def set_connections(self, key: str,
        conns: ConnectionsABC | Iterable[Iterable[XEndPointRefABC]]) -> None:
        """Set the connections object for the given key"""
        raise NotImplementedError("GCGraphABC.set_connections must be overridden")

    @abstractmethod
    def set_interface(self, key: str, iface: InterfaceABC | Iterable[EndPointType]) -> None:
        """Set the interface object for the given key"""
        raise NotImplementedError("GCGraphABC.set_interface must be overridden")
