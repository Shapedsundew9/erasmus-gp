"""
Builtin graph classes for the Connection Graph.

This module provides classes for creating and managing Connection Graphs,
which are used to represent graph structures in the GC system.

GC nodes have an input property, an output property and a property called a 'connection graph'
which defines edges between the inputs, outputs, GCA (inputs and outputs) and GCB (inputs and
outputs) if present. These are the python function parameters, local variables and return values.
There are several types of connection graph:
    - Conditional
        - If-then
        - If-then-else
    - Empty
    - Loop
        - For
        - While
    - Standard

The inputs and output properties are interface objects. Interface objects are lists of endpoint
objects which come in many different types defined by an unsigned 32 bit integer (and
equivalent python type). Interfaces are either sources or destinations.
The connection graph property of the GC defines the point to point
connections between the endpoints of all the interfaces in a GC node subject to certain rules.

Using the nomenclature:
    - Is: GC Node input source interface
    - Fd: GC Node conditional destination interface
    - Ld: GC Node loop iterable destination interface
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
    - Destination endpoints must have 1 and only 1 connection to it.
    - Interfaces may have 0 to MAX_NUM_ENDPOINTS (inclusive) endpoints
    - MAX_NUM_ENDPOINTS == 255
    - Fd, Ld, Wd and Ls must have exactly 1 endpoint in the interface
    - Pd must have the same interface endpoint number, order and types as Od.
    - Any Is endpoint may be a source to any destination endpoint with the exception of Wd
    - Any source endpoint that is not connected to any other destination endpoint is connected
      to the Ud interface.
    - Codon nodes support all types of connection graphs. GCA and GCB, as needed, are implicit.
    - An interface still exists even if it has zero endpoints.
    - "x can only connect to y" does not restrict what can connect to y.
    - "y can connect to x" does not imply that x can connect to y.

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
    - An empty graph has no connections

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
"""

from __future__ import annotations

from collections.abc import Collection, Iterator
from itertools import chain
from pprint import pformat
from random import choice, shuffle
from typing import Any

from egpcommon.common import NULL_FROZENSET
from egpcommon.egp_log import DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_constants import (
    CPI,
    ROW_CLS_INDEXED,
    ROW_CLS_INDEXED_SET,
    SOURCE_ROW_MAP,
    DstIfKey,
    DstRow,
    EndPointClass,
    EPClsPostfix,
    JSONCGraph,
    Row,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.interface import NULL_INTERFACE, Interface, SrcInterface
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
# This pattern involves creating a logger instance using the egp_logger function,
# and setting up boolean flags to check if certain logging levels (DEBUG, VERIFY, CONSISTENCY)
# are enabled. This allows for conditional logging based on the configured log level.
_logger: Logger = egp_logger(name=__name__)


# Constants
_UNDER_ROW_CLS_INDEXED: tuple[str, ...] = tuple("_" + row for row in ROW_CLS_INDEXED)
_UNDER_ROW_DST_INDEXED: tuple[str, ...] = tuple("_" + row + EPClsPostfix.DST for row in DstRow)
_UNDER_DST_KEY_DICT: dict[str | Row, str] = {row: "_" + row + EPClsPostfix.DST for row in DstRow}
_UNDER_SRC_KEY_DICT: dict[str | Row, str] = {row: "_" + row + EPClsPostfix.SRC for row in SrcRow}
_UNDER_KEY_DICT: dict[str | DstIfKey | SrcIfKey, str] = {
    k: ("_" + k) for k in chain(DstIfKey, SrcIfKey)
}

# NOTE: There are a lot of duplicate frozensets in this module. They have not been reduced to
# constants because they are used in different contexts and it is not clear that they
# can be safely reused as they are in different contexts (and future changes may then
# propagate inappropriately).


def valid_src_rows(graph_type: CGraphType) -> dict[DstRow, frozenset[SrcRow]]:
    """Return a dictionary of valid source rows for the given graph type.

    Args:
        graph_type: The type of graph to validate.
    """
    retval: dict[DstRow, frozenset[SrcRow]] = {}
    match graph_type:
        case CGraphType.IF_THEN:
            retval = {
                DstRow.A: frozenset({SrcRow.I}),
                DstRow.F: frozenset({SrcRow.I}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.P: frozenset({SrcRow.I}),
            }
        case CGraphType.IF_THEN_ELSE:
            retval = {
                DstRow.A: frozenset({SrcRow.I}),
                DstRow.F: frozenset({SrcRow.I}),
                DstRow.B: frozenset({SrcRow.I}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.P: frozenset({SrcRow.I, SrcRow.B}),
                DstRow.U: frozenset({SrcRow.I}),
            }
        case CGraphType.EMPTY:
            retval = {
                DstRow.O: NULL_FROZENSET,
            }
        case CGraphType.FOR_LOOP:
            retval = {
                DstRow.A: frozenset({SrcRow.I, SrcRow.L}),
                DstRow.L: frozenset({SrcRow.I}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.P: frozenset({SrcRow.I}),
            }
        case CGraphType.WHILE_LOOP:
            retval = {
                DstRow.A: frozenset({SrcRow.I, SrcRow.L}),
                DstRow.L: frozenset({SrcRow.I}),
                DstRow.W: frozenset({SrcRow.A}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.P: frozenset({SrcRow.I}),
            }
        case CGraphType.STANDARD:
            retval = {
                DstRow.A: frozenset({SrcRow.I}),
                DstRow.B: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A, SrcRow.B}),
            }
        case CGraphType.PRIMITIVE:
            retval = {
                DstRow.A: frozenset({SrcRow.I}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
            }
        case CGraphType.UNKNOWN:  # The superset case
            retval = {
                DstRow.A: frozenset({SrcRow.I, SrcRow.L}),
                DstRow.B: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.F: frozenset({SrcRow.I}),
                DstRow.L: frozenset({SrcRow.I}),
                DstRow.W: frozenset({SrcRow.A}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A, SrcRow.B}),
                DstRow.P: frozenset({SrcRow.I, SrcRow.B}),
                # FIXME: Can L ever not be connected?
                DstRow.U: frozenset({SrcRow.A, SrcRow.I, SrcRow.L, SrcRow.B}),
            }
        case _:
            retval = {}

    # Add the U row to the dictionary (super set of all sources)
    retval[DstRow.U] = frozenset({src for srcs in retval.values() for src in srcs})
    return retval


def valid_dst_rows(graph_type: CGraphType) -> dict[SrcRow, frozenset[DstRow]]:
    """Return a dictionary of valid destination rows for the given graph type."""
    match graph_type:
        case CGraphType.IF_THEN:
            return {
                SrcRow.I: frozenset({DstRow.A, DstRow.F, DstRow.O, DstRow.P}),
                SrcRow.A: frozenset({DstRow.O}),
            }
        case CGraphType.IF_THEN_ELSE:
            return {
                SrcRow.I: frozenset({DstRow.A, DstRow.F, DstRow.B, DstRow.P, DstRow.O}),
                SrcRow.A: frozenset({DstRow.O}),
                SrcRow.B: frozenset({DstRow.P}),
            }
        case CGraphType.EMPTY:
            return {
                SrcRow.I: NULL_FROZENSET,
            }
        case CGraphType.FOR_LOOP:
            return {
                SrcRow.I: frozenset({DstRow.A, DstRow.L, DstRow.O, DstRow.P}),
                SrcRow.L: frozenset({DstRow.A}),
                SrcRow.A: frozenset({DstRow.O}),
            }
        case CGraphType.WHILE_LOOP:
            return {
                SrcRow.I: frozenset({DstRow.A, DstRow.L, DstRow.O, DstRow.P}),
                SrcRow.L: frozenset({DstRow.A}),
                SrcRow.A: frozenset({DstRow.O, DstRow.W}),
            }
        case CGraphType.STANDARD:
            return {
                SrcRow.I: frozenset({DstRow.A, DstRow.B, DstRow.O}),
                SrcRow.A: frozenset({DstRow.B, DstRow.O}),
                SrcRow.B: frozenset({DstRow.O}),
            }
        case CGraphType.PRIMITIVE:
            return {
                SrcRow.I: frozenset({DstRow.A, DstRow.O}),
                SrcRow.A: frozenset({DstRow.O}),
            }
        case CGraphType.UNKNOWN:  # The superset case
            return {
                SrcRow.I: frozenset(
                    {DstRow.A, DstRow.B, DstRow.F, DstRow.L, DstRow.O, DstRow.P, DstRow.W, DstRow.U}
                ),
                # FIXME: Can L ever not be connected?
                SrcRow.L: frozenset({DstRow.A, DstRow.U}),
                SrcRow.A: frozenset({DstRow.B, DstRow.O, DstRow.W, DstRow.U}),
                SrcRow.B: frozenset({DstRow.O, DstRow.P, DstRow.U}),
            }
        case _:
            # There are no valid rows for this graph type (likely RESERVED)
            return {}


def valid_rows(graph_type: CGraphType) -> frozenset[Row]:
    """Return a dictionary of valid rows for the given graph type.

    Args:
        graph_type: The type of graph to validate.

    Returns:
        A dictionary of valid rows for the given graph type.
    """
    return frozenset(valid_dst_rows(graph_type).keys()) | frozenset(
        valid_src_rows(graph_type).keys()
    )


def valid_jcg(jcg: JSONCGraph) -> bool:
    """Validate a JSON connection graph.

    Args:
        jcg: The JSON connection graph to validate.

    Returns:
        True if the JSON connection graph is valid, False otherwise.
    """
    # Check that all keys are valid
    for key in jcg.keys():
        if key not in DstRow:
            raise ValueError(f"Invalid key in JSON connection graph: {key}")

    # Check that all values are valid
    for key, epts in jcg.items():
        if not isinstance(epts, list):
            raise TypeError(f"Invalid value in JSON connection graph: {epts}")

    # Check that connectivity is valid
    for dst, vsr in valid_src_rows(c_graph_type(jcg)).items():
        if dst not in jcg:
            raise ValueError(f"Missing destination row in JSON connection graph: {dst}")
        for src in jcg[dst]:
            if not isinstance(src, list):
                raise TypeError("Expected a list of defining an endpoint.")
            srow = src[CPI.ROW]
            if not isinstance(srow, str):
                raise TypeError("Expected a destination row")
            row: SrcRow | None = SOURCE_ROW_MAP.get(srow)
            idx = src[CPI.IDX]
            ept = src[CPI.TYP]
            if row is None:
                raise ValueError("Expected a valid source row")
            if not isinstance(idx, int):
                raise TypeError("Expected an integer index")
            if not isinstance(ept, str):
                raise TypeError("Expected a list of endpoint int types")

            if row not in vsr:
                raise ValueError(
                    f"Invalid source row in JSON connection graph: {row} for destination {dst}"
                )
            if not 0 <= idx < 256:
                raise ValueError(
                    f"Index out of range for JSON connection graph: {idx} for destination {dst}"
                )
            if not ept in types_def_store:
                raise ValueError(
                    f"Invalid endpoint type in JSON connection graph: {ept} for destination {dst}"
                )

    return True


# Constants
CGT_VALID_SRC_ROWS = {cgt: valid_src_rows(cgt) for cgt in CGraphType}
CGT_VALID_DST_ROWS = {cgt: valid_dst_rows(cgt) for cgt in CGraphType}
CGT_VALID_ROWS = {cgt: valid_rows(cgt) for cgt in CGraphType}


def json_cgraph_to_interfaces(jcg: JSONCGraph) -> dict[str, Interface]:
    """Convert a JSONCGraph to a dictionary of Interface objects.

    This function transforms a JSON Connection Graph structure into a dictionary
    of Interface objects that can be used to initialize a CGraph instance.

    Args:
        jcg: The JSON connection graph to convert.

    Returns:
        A dictionary mapping interface names (e.g., 'Ad', 'Is') to Interface objects.

    Raises:
        ValueError: If the JSON connection graph is invalid.
        TypeError: If the input types are incorrect.
    """
    # Validate the JSON connection graph first
    if _logger.isEnabledFor(level=DEBUG):
        valid_jcg(jcg)

    # Create source endpoint dictionary for building source interfaces
    src_ep_dict: dict[SrcRow, dict[int, EndPoint]] = {}

    # Create destination interfaces from JSON structure
    interfaces: dict[str, Interface] = {}

    # Process each destination row in the JSON graph
    for dst_row, iface_def in jcg.items():
        # Create destination interface
        dst_iface_key = dst_row + EPClsPostfix.DST
        dst_interface = Interface(iface_def, row=DstRow(dst_row))
        interfaces[dst_iface_key] = dst_interface

        # Build source endpoint references for each destination endpoint
        for idx, ep in enumerate(dst_interface.endpoints):
            for ref in ep.refs:
                # Create source endpoints that correspond to destination references
                src_row = SrcRow(ref[0])
                src_idx = ref[1]

                src_ep_dict.setdefault(src_row, {})
                if src_idx in src_ep_dict[src_row]:
                    # Source endpoint already exists, validate type consistency and add reference
                    src_ep = src_ep_dict[src_row][src_idx]
                    if src_ep.typ != ep.typ:
                        raise ValueError(
                            f"Type inconsistency for source endpoint {src_row},{src_idx}: "
                            f"existing type '{src_ep.typ.name}' "
                            f"conflicts with new type '{ep.typ.name}'"
                        )
                    refs = src_ep.refs
                    assert isinstance(refs, list), "Expected refs to be a list."
                    refs.append([dst_row, idx])
                else:
                    # Create new source endpoint
                    assert isinstance(
                        src_idx, int
                    ), f"Expected an integer index, got {type(src_idx)}"
                    src_ep_dict[src_row][src_idx] = EndPoint(
                        src_row,
                        src_idx,
                        EndPointClass.SRC,
                        ep.typ,
                        refs=[[dst_row, idx]],
                    )

    # Create source interfaces from the collected source endpoints
    for src_row, eps in src_ep_dict.items():
        src_iface_key = src_row + EPClsPostfix.SRC
        interfaces[src_iface_key] = SrcInterface(sorted(eps.values()))

    return interfaces


def c_graph_type(jcg: JSONCGraph | CGraph) -> CGraphType:
    """Identify the connection graph type from the JSON graph."""
    if _logger.isEnabledFor(level=DEBUG):
        if DstRow.O not in jcg:
            raise ValueError("All connection graphs must have a row O.")
        if not (DstRow.U in jcg or isinstance(jcg, CGraph)):
            raise ValueError("All JSON connection graphs must have a row U.")
        if DstRow.F in jcg:
            if DstRow.A not in jcg:
                raise ValueError("All conditional connection graphs must have a row A.")
            if DstRow.P not in jcg:
                raise ValueError("All conditional connection graphs must have a row P.")
            return CGraphType.IF_THEN_ELSE if DstRow.B in jcg else CGraphType.IF_THEN
        if DstRow.L in jcg:
            if DstRow.A not in jcg:
                raise ValueError("All loop connection graphs must have a row A.")
            if DstRow.P not in jcg:
                raise ValueError("All loop connection graphs must have a row P.")
            return CGraphType.WHILE_LOOP if DstRow.W in jcg else CGraphType.FOR_LOOP
        if DstRow.B in jcg:
            if DstRow.A not in jcg:
                raise ValueError("A standard graph must have a row A.")
            return CGraphType.STANDARD

    # Same as above but without the checks
    if DstRow.F in jcg:
        return CGraphType.IF_THEN_ELSE if DstRow.B in jcg else CGraphType.IF_THEN
    if DstRow.L in jcg:
        return CGraphType.WHILE_LOOP if DstRow.W in jcg else CGraphType.FOR_LOOP
    if DstRow.B in jcg:
        return CGraphType.STANDARD
    return CGraphType.PRIMITIVE if DstRow.A in jcg else CGraphType.EMPTY


class CGraph(FreezableObject, Collection):
    """Builtin graph class for the Connection Graph.

    Frozen graphs are created once and then never modified.
    """

    # Capture the slot names at class definition time. This ensures that
    # __slots__ and the __init__ loop use the exact same list.
    __slots__ = _UNDER_ROW_CLS_INDEXED + ("_hash",)

    def __init__(self, graph: dict[str, Interface]) -> None:
        """Initialize the Connection Graph."""
        FreezableObject.__init__(self, False)

        # Set defaults
        for key in _UNDER_ROW_CLS_INDEXED:
            setattr(self, key, NULL_INTERFACE)

        # Process interface definitions
        for iface, iface_def in graph.items():
            if isinstance(iface_def, Interface):
                assert iface in ROW_CLS_INDEXED_SET, f"Invalid interface key: {iface}"
                under_iface: str = _UNDER_KEY_DICT[iface]
                setattr(self, under_iface, iface_def)
            else:
                raise TypeError(f"Invalid interface definition for {iface}: {iface_def}")

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0

    def __contains__(self, key: object) -> bool:
        """Check if the interface exists in the Connection Graph.

        Args:
            key (str): May be a row or a row with class postfix (e.g. 'Fd', 'Ad', etc.).
        """
        assert isinstance(key, str), f"Key must be a string, got {type(key)}"
        if len(key) == 1:
            return (
                getattr(self, _UNDER_DST_KEY_DICT.get(key, "_"), NULL_INTERFACE)
                is not NULL_INTERFACE
                or getattr(self, _UNDER_SRC_KEY_DICT.get(key, "_"), NULL_INTERFACE)
                is not NULL_INTERFACE
            )
        return getattr(self, _UNDER_KEY_DICT.get(key, "_"), NULL_INTERFACE) is not NULL_INTERFACE

    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""
        if self.is_frozen():
            raise RuntimeError("Cannot modify a frozen connection graph.")
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        setattr(self, _UNDER_KEY_DICT.get(key, "_"), NULL_INTERFACE)

    def __eq__(self, value: object) -> bool:
        """Check equality of Connection Graphs."""
        if not isinstance(value, CGraph):
            return False
        # Compare all interfaces in the graph
        for key in _UNDER_ROW_CLS_INDEXED:
            if getattr(self, key) != getattr(value, key):
                return False
        return True

    def __hash__(self) -> int:
        """Return the hash of the Connection Graph."""
        if self.is_frozen():
            # Use the persistent hash if the interface is frozen. Hash is defined in self.freeze()
            return self._hash
        # If not frozen, calculate the hash dynamically
        return hash(tuple(getattr(self, key) for key in _UNDER_ROW_CLS_INDEXED))

    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        return getattr(self, _UNDER_KEY_DICT.get(key, "_"))

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the keys of the Connection Graph."""
        return (
            key
            for key in ROW_CLS_INDEXED
            if getattr(self, _UNDER_KEY_DICT.get(key, "_"), NULL_INTERFACE) is not NULL_INTERFACE
        )

    def __len__(self) -> int:
        """Return the number of interfaces in the Connection Graph."""
        return sum(
            1
            for key in ROW_CLS_INDEXED
            if getattr(self, _UNDER_KEY_DICT.get(key, "_"), NULL_INTERFACE) is not NULL_INTERFACE
        )

    def __repr__(self) -> str:
        """Return a string representation of the Connection Graph."""
        return pformat(self.to_json(), indent=4, width=120)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the endpoint with the given key."""
        if self.is_frozen():
            raise RuntimeError("Cannot modify a frozen connection graph.")
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        if not isinstance(value, Interface):
            raise TypeError(f"Value must be an Interface, got {type(value)}")
        setattr(self, _UNDER_KEY_DICT.get(key, "_"), value)

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable, i.e. all destinations are connected."""
        if self.is_frozen():
            # Destination end points are guaranteed to be connected if they are frozen.
            return True
        difs = (getattr(self, key) for key in _UNDER_ROW_DST_INDEXED)
        return all(not iface.unconnected_eps() for iface in difs if iface is not NULL_INTERFACE)

    def to_json(self, json_c_graph: bool = False) -> dict | JSONCGraph:
        """Convert the Connection Graph to a JSON-compatible dictionary."""
        jcg: JSONCGraph = {}
        for key in DstRow:
            iface: Interface = getattr(self, _UNDER_DST_KEY_DICT[key])
            if iface is not NULL_INTERFACE:
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
            chain.from_iterable(
                iface.unconnected_eps() for iface in ifaces if iface is not NULL_INTERFACE
            )
        )
        shuffle(unconnected)

        # Connect the unconnected endpoints in a random order
        # First find the set of valid source rows for this graph type.
        vsrc_rows = valid_src_rows(c_graph_type(self))
        i_iface: Interface = getattr(self, "_Is")
        for dep in unconnected:
            # Gather all the viable source interfaces for this destination endpoint.
            valid_src_rows_for_dst = vsrc_rows[DstRow(dep.row)]
            vifs = (getattr(self, _UNDER_SRC_KEY_DICT[row]) for row in valid_src_rows_for_dst)
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
                    assert isinstance(i_iface.endpoints, list), "Input interface must be a list"
                    i_iface.endpoints.append(sep)
                # Connect the destination endpoint to the source endpoint
                dep.connect(sep)

    def copy(self) -> CGraph:
        """Return a modifiable shallow copy of the Connection Graph."""
        # Create a new CGraph instance with the same interfaces
        return CGraph({key[1:]: getattr(self, key) for key in _UNDER_ROW_CLS_INDEXED})

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
            if iface is not NULL_INTERFACE:
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
        if self.is_frozen() or self.is_stable():
            self._verify_all_destinations_connected()

        # Call parent verify
        super().verify()

    def _verify_interface_presence(
        self, graph_type: CGraphType, valid_rows_set: frozenset[Row]
    ) -> None:
        """Verify that only valid interfaces for the graph type are present."""
        for key in ROW_CLS_INDEXED:
            iface = getattr(self, _UNDER_KEY_DICT[key])
            if iface is not NULL_INTERFACE:
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
        """Verify that endpoint connections follow the graph type rules."""
        # Check destination endpoints connect to valid source rows
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is NULL_INTERFACE:
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
            if src_iface is NULL_INTERFACE:
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
        """Verify that F, L, W interfaces have at most 1 endpoint."""
        for row in [DstRow.F, DstRow.L, DstRow.W]:
            iface = getattr(self, _UNDER_DST_KEY_DICT[row])
            if iface is not NULL_INTERFACE:
                self.value_error(
                    len(iface) <= 1,
                    f"Interface {row}d must have at most 1 endpoint, found {len(iface)}",
                )

        # L source interface must also have at most 1 endpoint
        ls_iface = getattr(self, _UNDER_SRC_KEY_DICT[SrcRow.L])
        if ls_iface is not NULL_INTERFACE:
            self.value_error(
                len(ls_iface) <= 1,
                f"Interface Ls must have at most 1 endpoint, found {len(ls_iface)}",
            )

    def _verify_type_consistency(self) -> None:
        """Verify that connected endpoints have matching types."""
        # Check all destination endpoints
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is NULL_INTERFACE:
                continue

            for dst_ep in dst_iface.endpoints:
                if dst_ep.is_connected():
                    for ref in dst_ep.refs:
                        ref_row_str, ref_idx = ref
                        # Get the source endpoint
                        src_iface = getattr(self, _UNDER_SRC_KEY_DICT[ref_row_str])
                        self.value_error(
                            src_iface is not NULL_INTERFACE,
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
        """Verify that all destination endpoints are connected."""
        unconnected: list[str] = []
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is NULL_INTERFACE:
                continue

            for ep in dst_iface.endpoints:
                if not ep.is_connected():
                    unconnected.append(f"{dst_row}{ep.idx}")

        self.value_error(
            len(unconnected) == 0,
            f"Stable/frozen graph has unconnected destination endpoints: {unconnected}",
        )
