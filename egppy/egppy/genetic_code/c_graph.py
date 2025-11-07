"""
This module provides classes for creating and managing Connection Graphs (CGraph),
which are used to represent graph structures in the Genetic Code (GC) system.

Genetic Codes, GCs, have a property called a 'connection graph'
(a CGraphABC instance) which defines the connectivity between the constituent GC A and GC B
genetic codes and the GC's inputs and outputs. In the connection graph, edges arer called
connections and are directed, nodes are called
end points and come in two classes. A source endpoint and a destination endpoints. The class
of the end point defines at what end of a connection the endpoint resides. An in-order
collection of end points with the same row and end point class is called an interface and
thus an interface is also either a source or a destination interface.
Connections are defined by references stored in the end points. A source endpoint
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

Interfaces are identified by a two characters: A Row character and a Class character.
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
representations for storing end point data and connections. These representations are optimized
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
    - Endpoints can only be connected to end points of the same or a compatible type.
    - Source endpoints may be connected to 0, 1 or multiple destination endpoints.
    - Destination endpoints must have 1 and only 1 connection to it to be stable.
    - Destination endpoints may only be unconnected (have no connections) in unstable graphs.
    - Interfaces may have 0 to MAX_NUM_ENDPOINTS (inclusive) endpoints
    - MAX_NUM_ENDPOINTS == 255
    - Fd, Ld, Wd and Ls, when present, must have exactly 1 endpoint in the interface
    - Pd must have the same interface, i.e. endpoint number, order and types as Od.
    - Any Is endpoint may be a source to any destination endpoint with the exception of Wd
    - Any source endpoint that is not connected to any other destination endpoint is connected
      to the Ud interface in a JSON Connection Graph representation.
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

from collections.abc import Iterator
from itertools import chain
from pprint import pformat
from random import choice, shuffle

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import VERIFY, Logger, egp_logger
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import (
    _UNDER_DST_KEY_DICT,
    _UNDER_KEY_DICT,
    _UNDER_ROW_CLS_INDEXED,
    _UNDER_ROW_DST_INDEXED,
    _UNDER_SRC_KEY_DICT,
    ROW_CLS_INDEXED,
    ROW_CLS_INDEXED_SET,
    DstRow,
    EndPointClass,
    JSONCGraph,
    Row,
    SrcRow,
)
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.end_point_abc import EndpointMemberType
from egppy.genetic_code.interface import ROW_SET, Interface, InterfaceABC
from egppy.genetic_code.json_cgraph import (
    CGT_VALID_DST_ROWS,
    CGT_VALID_ROWS,
    CGT_VALID_SRC_ROWS,
    c_graph_type,
    valid_src_rows,
)

# Standard EGP logging pattern
# This pattern involves creating a logger instance using the egp_logger function,
# and setting up boolean flags to check if certain logging levels (DEBUG, VERIFY, CONSISTENCY)
# are enabled. This allows for conditional logging based on the configured log level.
_logger: Logger = egp_logger(name=__name__)


class CGraph(CommonObj, CGraphABC):
    """Mutable CGraph class."""

    # Capture the slot names at class definition time. This ensures that
    # __slots__ and the __init__ loop use the exact same list.
    __slots__ = _UNDER_ROW_CLS_INDEXED + ("_hash",)

    def __init__(self, graph: dict[str, list[EndpointMemberType]] | CGraphABC) -> None:
        """Initialize the Connection Graph.

        A full copy of all data is made from the provided graph to ensure independence.
        """
        super().__init__()

        # Set all interfaces from the provided graph.
        # Note that this is a mutable instance so a full copy of the initializing
        # interfaces are needed (but the graph may not be stable nor valid).
        # In the implementation there is a member slot for every possible interface
        # with the two character interface name preceded by an underscore (e.g. _Is,
        # _Fd, _Ad, etc.). The python object None is used to indicate that an interface
        # does not exist in this graph.
        for key in ROW_CLS_INDEXED:
            iface_def = Interface(graph[key]) if key in graph else None
            assert isinstance(
                iface_def, (InterfaceABC, type(None))
            ), f"Invalid interface definition for {key}: {iface_def}"
            setattr(self, _UNDER_KEY_DICT[key], iface_def)

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0

    def __contains__(self, key: object) -> bool:
        """Check if the interface exists in the Connection Graph.

        Args:
            key (str): May be a row or a row with class postfix (e.g. 'Fd', 'Ad', etc.).
        """
        assert isinstance(key, str), f"Key must be a string, got {type(key)}"
        if len(key) == 1:
            exists = False
            if key not in ROW_SET:
                raise KeyError(f"Invalid Connection Graph key: {key}")
            if key in DstRow:
                exists = getattr(self, _UNDER_DST_KEY_DICT[key]) is not None
            if key in SrcRow:
                exists = exists or getattr(self, _UNDER_SRC_KEY_DICT[key]) is not None
            return exists
        if key not in ROW_CLS_INDEXED_SET:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        return getattr(self, _UNDER_KEY_DICT[key]) is not None

    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""
        if key not in ROW_CLS_INDEXED_SET:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        setattr(self, _UNDER_KEY_DICT[key], None)

    def __eq__(self, value: object) -> bool:
        """Check equality of Connection Graphs."""
        if not isinstance(value, CGraphABC):
            return False
        return hash(self) == hash(value)

    def __hash__(self) -> int:
        """Return the hash of the Connection Graph.
        NOTE: All CGraphABC with the same state must return the same hash value.
        """
        return hash(tuple(hash(iface) for iface in self.values()))

    def __getitem__(self, key: str) -> InterfaceABC:
        """Get the interface with the given key."""
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        value = getattr(self, _UNDER_KEY_DICT[key])
        if value is None:
            raise KeyError(f"Connection Graph key not set: {key}")
        return value

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the Interfaces of the Connection Graph."""
        return (key for key in ROW_CLS_INDEXED if getattr(self, _UNDER_KEY_DICT[key]) is not None)

    def __len__(self) -> int:
        """Return the number of interfaces in the Connection Graph."""
        return sum(1 for key in _UNDER_ROW_CLS_INDEXED if getattr(self, key) is not None)

    def __repr__(self) -> str:
        """Return a string representation of the Connection Graph."""
        return pformat(self.to_json(), indent=4, width=120)

    def __setitem__(self, key: str, value: InterfaceABC) -> None:
        """Set the interface with the given key."""
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        if not isinstance(value, InterfaceABC):
            raise TypeError(f"Value must be an Interface, got {type(value)}")
        setattr(self, _UNDER_KEY_DICT[key], value)

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable, i.e. all destinations are connected."""
        difs = (getattr(self, key) for key in _UNDER_ROW_DST_INDEXED)
        return all(not iface.unconnected_eps() for iface in difs if iface is not None)

    def graph_type(self) -> CGraphType:
        """Identify and return the type of this connection graph."""
        return c_graph_type(self)

    def to_json(self, json_c_graph: bool = False) -> dict | JSONCGraph:
        """Convert the Connection Graph to a JSON-compatible dictionary."""
        jcg: JSONCGraph = {}
        for key in DstRow:
            iface: Interface = getattr(self, _UNDER_DST_KEY_DICT[key])
            if iface is not None:
                jcg[key] = iface.to_json(json_c_graph=json_c_graph)
        return jcg

    def connect_all(self, if_locked: bool = True) -> None:
        """
        Connect all unconnected destination endpoints in the Connection Graph to randomly
        selected valid source endpoints.

        This method iterates through all unconnected destination endpoints in the graph and randomly
        connects each to a valid source endpoint. The validity of source endpoints is determined by
        the graph type's structural rules.

        Args:
            if_locked (bool): If True, prevents the creation of new input interface endpoints.
                If False, allows extending the input interface ('I') with new endpoints when needed
                and when 'I' is a valid source row for the destination. Defaults to True.

        Returns:
            None: Modifies the graph in-place by establishing connections between endpoints.

        Process:
            1. Collects all unconnected destination endpoints from all destination interfaces
            2. Shuffles them to ensure random connection order
            3. For each unconnected destination endpoint:
                - Identifies valid source rows based on graph type rules
                - Finds all source endpoints matching the destination's type
                - If if_locked is False and 'I' is a valid source, may create a new input endpoint
                - Randomly selects and connects to a valid source endpoint
                - Creates new input interface endpoint if selected and not locked

        Note:
            - Source endpoint selection respects type compatibility (sep.typ == dep.typ)
            - Graph type rules define which source rows can connect to which destination rows
            - New input interface endpoints are only added when if_locked=False
            and structurally valid
        """
        # Make a list of unconnected endpoints and shuffle it
        ifaces = (getattr(self, key) for key in _UNDER_ROW_DST_INDEXED)
        unconnected: list[EndPoint] = list(
            chain.from_iterable(iface.unconnected_eps() for iface in ifaces if iface is not None)
        )
        shuffle(unconnected)

        # Connect the unconnected endpoints in a random order
        # First find the set of valid source rows for this graph type.
        vsrc_rows = valid_src_rows(c_graph_type(self))
        i_iface: Interface = getattr(self, "_Is")
        for dep in unconnected:
            # Gather all the viable source interfaces for this destination endpoint.
            valid_src_rows_for_dst = vsrc_rows[DstRow(dep.row)]
            _vifs = (getattr(self, _UNDER_SRC_KEY_DICT[row]) for row in valid_src_rows_for_dst)
            vifs = (vif for vif in _vifs if vif is not None)
            # Gather all the source endpoints that match the type of the destination endpoint.
            vsrcs = [sep for vif in vifs for sep in vif if sep.typ == dep.typ]
            # If the interface of the GC is not fixed (i.e. it is not an empty GC) then
            # a new input interface endpoint is an option, BUT only if I is a valid source
            # for this destination row according to the graph type rules.
            len_is = len(i_iface)
            if not if_locked and SrcRow.I in valid_src_rows_for_dst:
                # Add a new input interface endpoint as a valid source option regardless of whether
                # there are other valid source endpoints. This prevents the sub-GC interfaces from
                # being completely dependent on each other if their types match. Sub-GC interfaces
                # that are not connected to each other at all result in a GC called a _harmony_.
                vsrcs.append(EndPoint(SrcRow.I, len_is, EndPointClass.SRC, dep.typ, []))
            if vsrcs:
                # Randomly choose a valid source endpoint
                sep: EndPoint = choice(vsrcs)
                # If it is a new input interface endpoint then add it to input interface
                if not if_locked and sep.idx == len_is and sep.row == SrcRow.I:
                    i_iface.endpoints.append(sep)
                # Connect the destination endpoint to the source endpoint
                dep.connect(sep)

    def get(self, key: str, default: InterfaceABC | None = None) -> InterfaceABC | None:
        """Get the interface with the given key, or return default if not found."""
        return getattr(self, _UNDER_KEY_DICT[key], default)

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of the Connection Graph.

        Returns:
            Iterator over interface keys.
        """
        return iter(self)

    def values(self) -> Iterator[InterfaceABC]:
        """Return an iterator over the interfaces of the Connection Graph.
        Returns:
            Iterator over interfaces.
        """
        return (
            getattr(self, key) for key in _UNDER_ROW_CLS_INDEXED if getattr(self, key) is not None
        )

    def items(self) -> Iterator[tuple[str, InterfaceABC]]:
        """Return an iterator over the (key, interface) pairs in the Connection Graph.
        Returns:
            Iterator over (key, interface) pairs.
        """
        for key in ROW_CLS_INDEXED:
            iface = getattr(self, _UNDER_KEY_DICT[key])
            if iface is not None:
                yield key, iface

    def stabilize(self, if_locked: bool = True) -> None:
        """Stablization involves making all the mandatory connections and
        connecting all the remaining unconnected destination endpoints.
        Destinations are connected to sources in a random order.
        Stabilization is not guaranteed to be successful unless if_locked is False
        in which case unconnected destinations create new source endpoints in the
        input interface as needed.

        After stabilization, check is_stable() to determine if all destinations
        were successfully connected.
        """
        self.connect_all(if_locked)
        if _logger.isEnabledFor(level=VERIFY):
            self.verify()

    def verify(self) -> None:
        """Verify the Connection Graph structure and connectivity rules.

        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.

        This method validates:
        - All interfaces are properly typed
        - Graph type identification is consistent
        - Interface presence matches graph type rules
        - Endpoint connectivity follows graph type rules
        - Type consistency across connections
        - Reference validity (endpoints reference existing endpoints)

        For stable graphs (frozen or explicitly stable):
        - All destination endpoints must be connected
        - All connections must follow the graph type rules

        For unstable graphs:
        - Connections are validated but may be incomplete

        Raises:
            ValueError: If any validation check fails.
            TypeError: If any type check fails.
        """
        # Verify all interfaces
        for key in _UNDER_ROW_CLS_INDEXED:
            iface = getattr(self, key)
            if iface is not None:
                self.type_error(
                    isinstance(iface, Interface),
                    f"Interface {key} must be an Interface, got {type(iface)}",
                )
                iface.verify()

        # Identify the graph type
        graph_type = c_graph_type(self)

        # Get valid rows for this graph type
        valid_rows_set = CGT_VALID_ROWS[graph_type]
        valid_src_rows_dict = CGT_VALID_SRC_ROWS[graph_type]
        valid_dst_rows_dict = CGT_VALID_DST_ROWS[graph_type]

        # Verify interfaces present match graph type rules
        self._verify_interface_presence(graph_type, valid_rows_set)

        # Verify endpoint connectivity rules
        self._verify_connectivity_rules(graph_type, valid_src_rows_dict, valid_dst_rows_dict)

        # Verify single endpoint rules for F, L, W interfaces
        self._verify_single_endpoint_interfaces()

        # Verify type consistency across connections
        self._verify_type_consistency()

        # For frozen or explicitly stable graphs, verify all destinations are connected
        if self.is_stable():
            self._verify_all_destinations_connected()

        # Call parent verify
        super().verify()

    def _verify_interface_presence(
        self, graph_type: CGraphType, valid_rows_set: frozenset[Row]
    ) -> None:
        """Verify that only valid interfaces for the graph type are present.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        for key in ROW_CLS_INDEXED:
            iface = getattr(self, _UNDER_KEY_DICT[key])
            if iface is not None:
                # Extract the row from the key (first character)
                row_str = key[0]
                self.value_error(
                    row_str in valid_rows_set,
                    f"Interface {key} is not valid for graph type {graph_type}. "
                    f"Valid rows: {valid_rows_set}",
                )

    def _verify_connectivity_rules(
        self,
        graph_type: CGraphType,
        valid_src_rows_dict: dict[DstRow, frozenset[SrcRow]],
        valid_dst_rows_dict: dict[SrcRow, frozenset[DstRow]],
    ) -> None:
        """Verify that endpoint connections follow the graph type rules.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        # Check destination endpoints connect to valid source rows
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is None:
                continue

            valid_srcs = valid_src_rows_dict.get(dst_row, frozenset())
            for ep in dst_iface.endpoints:
                if ep.is_connected():
                    for ref in ep.refs:
                        ref_row_str, ref_idx = ref
                        # Check that the source row is valid for this destination
                        self.value_error(
                            ref_row_str in valid_srcs,
                            f"Destination {dst_row}{ep.idx} connects to {ref_row_str}{ref_idx}, "
                            f"but {ref_row_str} is not a valid source for"
                            f" {dst_row} in {graph_type} graphs. "
                            f"Valid sources: {valid_srcs}",
                        )

        # Check source endpoints connect to valid destination rows
        for src_row in SrcRow:
            src_iface = getattr(self, _UNDER_SRC_KEY_DICT[src_row])
            if src_iface is None:
                continue

            valid_dsts = valid_dst_rows_dict.get(src_row, frozenset())
            for ep in src_iface.endpoints:
                if ep.is_connected():
                    for ref in ep.refs:
                        ref_row_str, ref_idx = ref
                        # Check that the destination row is valid for this source
                        self.value_error(
                            ref_row_str in valid_dsts,
                            f"Source {src_row}{ep.idx} connects to {ref_row_str}{ref_idx}, "
                            f"but {ref_row_str} is not a valid destination for "
                            f"{src_row} in {graph_type} graphs. "
                            f"Valid destinations: {valid_dsts}",
                        )

    def _verify_single_endpoint_interfaces(self) -> None:
        """Verify that F, L, W interfaces have at most 1 endpoint.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        for row in [DstRow.F, DstRow.L, DstRow.W]:
            iface = getattr(self, _UNDER_DST_KEY_DICT[row])
            if iface is not None:
                self.value_error(
                    len(iface) <= 1,
                    f"Interface {row}d must have at most 1 endpoint, found {len(iface)}",
                )

        # L source interface must also have at most 1 endpoint
        ls_iface = getattr(self, _UNDER_SRC_KEY_DICT[SrcRow.L])
        if ls_iface is not None:
            self.value_error(
                len(ls_iface) <= 1,
                f"Interface Ls must have at most 1 endpoint, found {len(ls_iface)}",
            )

    def _verify_type_consistency(self) -> None:
        """Verify that connected endpoints have matching types.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        # Check all destination endpoints
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is None:
                continue

            for dst_ep in dst_iface.endpoints:
                if dst_ep.is_connected():
                    for ref in dst_ep.refs:
                        ref_row_str, ref_idx = ref
                        # Get the source endpoint
                        src_iface = getattr(self, _UNDER_SRC_KEY_DICT[ref_row_str])
                        self.value_error(
                            src_iface is not None,
                            f"Destination {dst_row}{dst_ep.idx} references non-existent"
                            f" source interface {ref_row_str}s",
                        )
                        self.value_error(
                            ref_idx < len(src_iface),
                            f"Destination {dst_row}{dst_ep.idx} references {ref_row_str}{ref_idx}, "
                            f"but {ref_row_str}s only has {len(src_iface)} endpoints",
                        )
                        src_ep = src_iface[ref_idx]
                        # Verify type consistency
                        self.value_error(
                            dst_ep.typ == src_ep.typ,
                            f"Type mismatch: {dst_row}{dst_ep.idx} has type {dst_ep.typ} "
                            f"but connects to {ref_row_str}{ref_idx} with type {src_ep.typ}",
                        )

    def _verify_all_destinations_connected(self) -> None:
        """Verify that all destination endpoints are connected.
        This check applies to stable graphs only.
        """
        unconnected: list[str] = []
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is None:
                continue

            for ep in dst_iface.endpoints:
                if not ep.is_connected():
                    unconnected.append(f"{dst_row}{ep.idx}")

        self.value_error(
            len(unconnected) == 0,
            f"Stable/frozen graph has unconnected destination endpoints: {unconnected}",
        )
