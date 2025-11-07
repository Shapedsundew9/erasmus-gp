"""
Abstract Base Class for Connection Graphs.

This module defines the abstract interface that all Connection Graph implementations
must adhere to. It establishes the contract for graph operations while allowing
for different concrete implementations.

The abstract base class ensures consistency in the API across different graph types
and implementations while maintaining the flexibility to optimize specific graph
variants.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Collection, Iterator

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_constants import JSONCGraph
from egppy.genetic_code.interface_abc import InterfaceABC


class CGraphABC(Collection, CommonObjABC, metaclass=ABCMeta):
    """Abstract Base Class for Connection Graphs.

    This class defines the essential interface that all Connection Graph
    implementations must provide. It inherits from FreezableObject to support
    immutability when frozen, Collection for standard container operations,
    and CommonObjABC for validation methods.

    Connection Graphs represent the internal connectivity structure of genetic
    code nodes, defining how inputs, outputs, and internal components are
    connected through various interface types.
    """

    __slots__ = ()

    # Abstract Container Protocol Methods

    @abstractmethod
    def __contains__(self, key: object) -> bool:
        """Check if the interface exists in the Connection Graph.

        Args:
            key: Interface identifier, may be a row or row with class postfix.

        Returns:
            True if the interface exists, False otherwise.
        """
        raise NotImplementedError("CGraphABC.__contains__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the interface keys in the Connection Graph.

        Returns:
            Iterator over non-null interface keys.
        """
        raise NotImplementedError("CGraphABC.__iter__ must be overridden")

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of interfaces in the Connection Graph.

        Returns:
            Number of non-null interfaces.
        """
        raise NotImplementedError("CGraphABC.__len__ must be overridden")

    # Abstract Mapping Protocol Methods

    @abstractmethod
    def __getitem__(self, key: str) -> InterfaceABC:
        """Get the interface with the given key.

        Args:
            key: Interface identifier.

        Returns:
            The Interface object for the given key.

        Raises:
            KeyError: If the key is invalid.
        """
        raise NotImplementedError("CGraphABC.__getitem__ must be overridden")

    @abstractmethod
    def __setitem__(self, key: str, value: InterfaceABC) -> None:
        """Set the interface with the given key.

        Args:
            key: Interface identifier.
            value: Interface object to set.

        Raises:
            RuntimeError: If the graph is frozen.
            KeyError: If the key is invalid.
            TypeError: If value is not an Interface.
        """
        raise NotImplementedError("CGraphABC.__setitem__ must be overridden")

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        """Delete the interface with the given key.

        Args:
            key: Interface identifier.

        Raises:
            RuntimeError: If the graph is frozen.
            KeyError: If the key is invalid.
        """
        raise NotImplementedError("CGraphABC.__delitem__ must be overridden")

    # Abstract Graph State Methods

    @abstractmethod
    def get(self, key: str, default: InterfaceABC | None = None) -> InterfaceABC | None:
        """Get the interface with the given key, or return default if not found.

        Args:
            key: Interface identifier.
            default: Value to return if key is not found.

        Returns:
            The Interface object for the given key, or default if not found.
        """
        raise NotImplementedError("CGraphABC.get must be overridden")

    @abstractmethod
    def keys(self) -> Iterator[str]:
        """Return an iterator over the interface keys in the Connection Graph.

        Returns:
            Iterator over non-null interface keys.
        """
        raise NotImplementedError("CGraphABC.keys must be overridden")

    @abstractmethod
    def values(self) -> Iterator[InterfaceABC]:
        """Return an iterator over the interfaces in the Connection Graph.

        Returns:
            Iterator over non-null interfaces.
        """
        raise NotImplementedError("CGraphABC.values must be overridden")

    @abstractmethod
    def items(self) -> Iterator[tuple[str, InterfaceABC]]:
        """Return an iterator over the (key, interface) pairs in the Connection Graph.

        Returns:
            Iterator over (key, interface) pairs.
        """
        raise NotImplementedError("CGraphABC.items must be overridden")

    @abstractmethod
    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable.

        A stable graph has all destination endpoints connected to source endpoints.
        Frozen graphs are guaranteed to be stable.

        Returns:
            True if all destinations are connected, False otherwise.
        """
        raise NotImplementedError("CGraphABC.is_stable must be overridden")

    @abstractmethod
    def graph_type(self) -> CGraphType:
        """Identify and return the type of this connection graph.

        Returns:
            The CGraphType enum value representing this graph's type.
        """
        raise NotImplementedError("CGraphABC.graph_type must be overridden")

    # Abstract Serialization Methods

    @abstractmethod
    def to_json(self, json_c_graph: bool = False) -> dict | JSONCGraph:
        """Convert the Connection Graph to a JSON-compatible dictionary.

        Args:
            json_c_graph: If True, return a JSONCGraph format.

        Returns:
            JSON-compatible dictionary representation of the graph.
        """
        raise NotImplementedError("CGraphABC.to_json must be overridden")

    # Abstract Connection Management Methods

    @abstractmethod
    def connect_all(self, if_locked: bool = True) -> None:
        """Connect all unconnected destination endpoints to valid source endpoints.

        This method establishes connections between unconnected destination endpoints
        and available source endpoints according to the graph type rules.

        Args:
            if_locked: If True, prevents creation of new input interface endpoints.
                      If False, allows extending input interface when needed.
        """
        raise NotImplementedError("CGraphABC.connect_all must be overridden")

    @abstractmethod
    def stabilize(self, if_locked: bool = True) -> None:
        """Stabilize the graph by connecting all unconnected destinations.

        Stabilization ensures all mandatory connections are made and attempts
        to connect remaining unconnected destination endpoints.

        Args:
            if_locked: If True, prevents creation of new input interface endpoints.
                      If False, allows extending input interface as needed.
        """
        raise NotImplementedError("CGraphABC.stabilize must be overridden")

    # Abstract Equality and Hashing

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Check equality of Connection Graphs.

        Args:
            other: Object to compare with.

        Returns:
            True if graphs are equivalent, False otherwise.
        """
        raise NotImplementedError("CGraphABC.__eq__ must be overridden")

    @abstractmethod
    def __hash__(self) -> int:
        """Return the hash of the Connection Graph.

        For frozen graphs, should use a persistent hash.
        For unfrozen graphs, should calculate dynamically.
        Both must be equal for the same graph state.

        Returns:
            Hash value for the graph.
        """
        raise NotImplementedError("CGraphABC.__hash__ must be overridden")

    # Abstract String Representation

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of the Connection Graph.

        Returns:
            String representation suitable for debugging and logging.
        """
        raise NotImplementedError("CGraphABC.__repr__ must be overridden")
