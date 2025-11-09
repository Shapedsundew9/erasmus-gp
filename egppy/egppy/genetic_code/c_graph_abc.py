"""
Abstract Base Class for Connection Graphs.

This module defines the abstract interface that all Connection Graph implementations
must adhere to. It establishes the contract for graph operations while allowing
for different concrete implementations.

The abstract base class ensures consistency in the API across different graph types
and implementations while maintaining the flexibility to optimize specific graph
variants.

Genetic Codes, GCs, have a property called a 'connection graph'
(a CGraphABC instance) which defines the connectivity between the constituent GC A and GC B
genetic codes and the GC's inputs and outputs. In the connection graph, edges are called
connections and are directed, nodes are called
endpoints and come in two classes. A source endpoint and a destination endpoints. The class
of the endpoint defines at what end of a connection the endpoint resides. An in-order
collection of endpoints with the same row and endpoint class is called an interface and
thus an interface is also either a source or a destination interface.
Connections are defined by references stored in the endpoints. A source endpoint
can connect to multiple destination endpoints, while a destination endpoint can
only connect to a single source endpoint.

There are several types of connection graph:
    - Conditional
        - If-then
        - If-then-else
    - Empty
    - Loop
        - For
        - While
    - Standard
    - Primitive

The type of connection graph determines the rules for what interfaces exist and how they
can be connected.

All connection graphs may be in one of two states, stable or unstable. A stable connection graph
is one in which all destination endpoints are connected to a source endpoint. An unstable
connection graph is one in which at least one destination endpoint is not connected to any
source endpoint.

Interfaces are identified by a two character key: A Row character and a Class character.
The Row character identifies the interface's row (one of IFLWABOPU) and the Class character
identifies whether the interface is a source (s) or destination (d) interface.

There are two representations of connection graphs:
    - JSON Connection Graph format, JSONCGraph type
    - CGraphABC class instance
The JSON Connection Graph format is a compact representation suitable for serialization
and storage of stable connection graphs only. The format specifies only the destination
endpoints and their connections, including a unique to JSON format destination row U for
otherwise unconnected source endpoints if needed, this allows all sources to be represented.
The CGraphABC class provides a common interfaces a mutable connection graph class CGraph
and an immutable frozen connection graph class FrozenCGraph. Mutable connection graphs
may be stable or unstable which allows them to be modified incrementally. Immutable
connection graphs are always stable.
To be efficient for their intended use cases, both concrete classes have specific internal
representations for storing endpoint data and connections. These representations are optimized
for performance characteristics and trade-offs. Thus CGraphABC makes use of abstract base
classes for endpoints (EndPointABC) and interfaces (InterfaceABC).

Below are the rules governing the permitted interfaces and connections for each type of
connection graph. Unless otherwise stated, these rules apply to both stable and unstable graphs.

Using the nomenclature:
    - Is: GC Node input source interface
    - Fd: GC Node conditional destination interface
    - Ld: GC Node loop iterable destination interface (for both for and while loops)
    - Ls: GC Node loop object source interface
    - Wd: GC Node while loop object destination interface
    - Ad: GCA input interface as a destination in the GC Node graph
    - As: GCA output interface as a source in the GC Node graph
    - Bd: GCB input interface as a destination in the GC Node graph
    - Bs: GCB output interface as a source in the GC Node graph
    - Od: GC Node output destination interface
    - Pd: GC Node output destination interface alternate route (conditional False,
      zero iteration loop)
    - Ud: GC Node destination interface for otherwise unconnected source endpoints
      (JSON format only)

Common Rules
    - Endpoints can only be connected to endpoints of the same or a compatible type.
    - Source endpoints may be connected to 0, 1 or multiple destination endpoints.
    - Destination endpoints must have 1 and only 1 connection to it to be stable.
    - Destination endpoints may only be unconnected (have no connections) in unstable graphs.
    - Interfaces may have 0 to MAX_NUM_ENDPOINTS (inclusive) endpoints
    - MAX_NUM_ENDPOINTS == 255
    - Fd, Ld, Wd and Ls, if they exist, must have exactly 1 endpoint in the interface when stable.
    - Pd must have the same interface, i.e. endpoint number, order and types as Od.
    - Any Is endpoint may be a source to any destination endpoint with the exception of Wd
    - Any source endpoint that is not connected to any other destination endpoint is connected
      to the Ud interface in a JSON Connection Graph representation.
    - Ud only exists in JSON Connection Graph representations and only if there are
      unconnected source endpoints
    - An interface still exists even if it has zero endpoints.
    - "x can only connect to y" does not restrict what can connect to y.
    - "y can connect to x" does not imply that x can connect to y.
    - An empty interface has zero endpoints and is not the same as a non-existent interface.
    - Is and Od must exist (and so Pd must exist in graph types that have Pd)
    - Either both of As and Ad exist or neither exist
    - Either both of Bs and Bd exist or neither exist
    - Interfaces on the same row cannot connect to each other (e.g. Bs cannot connect to Bd)
    - References must be consistent, i.e. if a destination endpoint references a source endpoint,
      the source endpoint must also reference the destination endpoint. This is still just a
      single directed connection. (NB: This is to facilitate verification of integrity.)

Additional to the Common Rules Conditional If-Then graphs have the following rules
    - Must not have Ld, Wd, Bd, Bs or Ls interfaces
    - Only Is can connect to Fd
    - As can only connect to Od or Ud
    - Only Is can connect to Pd

Additional to the Common Rules Conditional If-Then-Else graphs have the following rules
    - Must not have Ld, Wd or Ls interfaces
    - Only Is can connect to Fd
    - As can only connect to Od or Ud
    - Bs can only connect to Pd or Ud

Additional to the Common Rules Empty graphs have the following rules
    - An empty graph only has Is and Od interfaces
    - May have a Ud interface (in JSON format only)
    - An empty graph has no connections (and is thus always unstable if Od has endpoints)

Additional to the Common Rules For-Loop graphs have the following rules
    - Must not have an Fd, Wd, Bs, or Bd interface
    - Only Is can connect to Ld
    - Ls can only connect to Ad
    - Ld must be an iterable compatible endpoint type.
    - Ls must be the object type returned by iterating Ld.
    - As can only connect to Od or Ud
    - Only Is can connect to Pd

Additional to the Common Rules While-Loop graphs have the following rules
    - Must not have an Fd, Bs or Bd interface
    - Only Is can connect to Ld
    - Ls can only connect to Ad
    - Only As can connect to Wd
    - Wd and Ls must be the same type as Ld
    - Is and As can connect to Od or Ud
    - Only Is can connect to Pd

Additional to the Common Rules Standard graphs have the following rules
    - Must not have an Fd, Ld, Wd, Ls or Pd interface
    - Bs can only connect to Od or Ud

Additional to the Common Rules Primitive connection graphs have the following rules
    - Must not have an Fd, Ld, Wd, Ls, Pd, Bd, Bs or Ud interfaces
    - All sources must be connected to destinations
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Collection, Iterator
from typing import Any

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_rnd_gen import EGPRndGen, egp_rng
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_constants import JSONCGraph
from egppy.genetic_code.interface_abc import InterfaceABC


class CGraphABC(Collection, CommonObjABC, metaclass=ABCMeta):
    """Abstract Base Class for Connection Graphs.

    This class defines the essential interface that all Connection Graph
    implementations must provide. It inherits Collection for standard container
    operations, and CommonObjABC for validation methods.

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
        Raises:
            KeyError: If the key is not a valid interface key.
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
    def to_json(self, json_c_graph: bool = False) -> dict[str, Any] | JSONCGraph:
        """Convert the Connection Graph to a JSON-compatible dictionary.

        Args:
            json_c_graph: If True, return a JSONCGraph format.

        Returns:
            JSON-compatible dictionary representation of the graph.
        """
        raise NotImplementedError("CGraphABC.to_json must be overridden")

    # Abstract Connection Management Methods

    @abstractmethod
    def connect_all(self, if_locked: bool = True, rng: EGPRndGen = egp_rng) -> None:
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
