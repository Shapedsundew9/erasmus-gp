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

from itertools import chain
from pprint import pformat
from random import choice, shuffle
from typing import Any, Iterable

from egpcommon.common import NULL_FROZENSET
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_constants import (
    CPI,
    DESTINATION_ROW_SET,
    ROW_CLS_INDEXED,
    ROW_CLS_INDEXED_SET,
    SOURCE_ROW_MAP,
    DstRow,
    EndPointClass,
    EPClsPostfix,
    JSONCGraph,
    Row,
    SrcRow,
)
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.interface import NULL_INTERFACE, Interface
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
# This pattern involves creating a logger instance using the egp_logger function,
# and setting up boolean flags to check if certain logging levels (DEBUG, VERIFY, CONSISTENCY)
# are enabled. This allows for conditional logging based on the configured log level.
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Constants
_UNDER_ROW_CLS_INDEXED: tuple[str, ...] = tuple("_" + row for row in ROW_CLS_INDEXED)
_UNDER_ROW_DST_INDEXED: tuple[str, ...] = tuple("_" + row + EPClsPostfix.DST for row in DstRow)


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


class CGraph(FreezableObject):
    """Builtin graph class for the Connection Graph.

    Frozen graphs are created once and then never modified.
    """

    # Capture the slot names at class definition time. This ensures that
    # __slots__ and the __init__ loop use the exact same list.
    __slots__ = _UNDER_ROW_CLS_INDEXED + ("_hash",)

    def __init__(self, graph: dict[str, Interface] | JSONCGraph) -> None:
        """Initialize the Connection Graph."""
        FreezableObject.__init__(self, False)

        # Set defaults
        for key in _UNDER_ROW_CLS_INDEXED:
            setattr(self, key, NULL_INTERFACE)

        # Iterate over the interface definitions in the graph.
        # NOTE: The keys for a JSONCGraph are just destination row letters but for
        # a dict of Interfaces they are the row letter and the class (e.g. 'Fd', 'Ad', 'Bs', etc.)
        src_ep_dict: dict[SrcRow, dict[int, EndPoint]] = {}
        json_flag = False
        for iface, iface_def in graph.items():
            if isinstance(iface_def, Interface):
                under_iface: str = "_" + iface
                assert iface in ROW_CLS_INDEXED_SET, f"Invalid interface key: {iface}"
                setattr(self, under_iface, iface_def)
            elif isinstance(iface_def, list):
                # Convert list to Interface
                # Since this must be a JSONCGraph the interface is a destination interface
                if not json_flag:
                    valid_jcg(graph)  # type: ignore
                    json_flag = True
                under_iface: str = "_" + iface + EPClsPostfix.DST
                assert iface in DESTINATION_ROW_SET, f"Invalid interface key: {iface}"
                assert isinstance(
                    iface_def, (list | tuple)
                ), f"Expected a list or tuple for interface {iface}, got {type(iface_def)}"
                setattr(self, under_iface, Interface(iface_def, row=DstRow(iface)))
                for idx, ep in enumerate(getattr(self, under_iface).endpoints):
                    # There may be 1 or 0 source endpoint references
                    assert isinstance(ep, EndPoint), f"Expected an EndPoint, got {type(ep)}"
                    for ref in ep.refs:
                        # Create a set of source endpoints for the destination endpoint
                        src_ep_dict.setdefault(SrcRow(ref[0]), {})
                        if ref[1] in src_ep_dict[SrcRow(ref[0])]:
                            src_ep = src_ep_dict[SrcRow(ref[0])][ref[1]]
                            refs = src_ep.refs
                            assert isinstance(refs, list), "Expected refs to be a list."
                            # Make sure both references are for the same type.
                            assert ep.typ == src_ep.typ, f"Type mismatch: {src_ep.typ} == {ep.typ}"
                            refs.append([iface, ep.idx])
                        else:
                            ri = ref[1]
                            assert isinstance(ri, int), f"Expected an integer index, got {type(ri)}"
                            src_ep_dict[SrcRow(ref[0])][ri] = EndPoint(
                                SrcRow(ref[0]),
                                int(ref[1]),
                                EndPointClass.SRC,
                                ep.typ,
                                [[iface, idx]],
                            )
            else:
                raise TypeError(f"Invalid interface definition for {iface}: {iface_def}")

        # If the graph is a JSONCGraph, we need to create the source interfaces
        # src_ep_dict will be empty if the graph parameter is a dict of Interfaces
        for src_row, eps in src_ep_dict.items():
            setattr(self, "_" + src_row + EPClsPostfix.SRC, Interface(sorted(eps.values())))

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0

    def __contains__(self, key: str) -> bool:
        """Check if the interface exists in the Connection Graph.

        Args:
            key (str): May be a row or a row with class postfix (e.g. 'Fd', 'Ad', etc.).
        """
        if len(key) == 1:
            return (
                getattr(self, "_" + key + EPClsPostfix.DST, NULL_INTERFACE) is not NULL_INTERFACE
                or getattr(self, "_" + key + EPClsPostfix.SRC, NULL_INTERFACE) is not NULL_INTERFACE
            )
        return getattr(self, "_" + key) is not NULL_INTERFACE

    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""
        if self.is_frozen():
            raise RuntimeError("Cannot modify a frozen connection graph.")
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        setattr(self, "_" + key, NULL_INTERFACE)

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
        return getattr(self, "_" + key)

    def __iter__(self) -> Iterable[str]:
        """Return an iterator over the keys of the Connection Graph."""
        return (key for key in ROW_CLS_INDEXED if getattr(self, "_" + key) is not NULL_INTERFACE)

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
        setattr(self, "_" + key, value)

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
            iface: Interface = getattr(self, "_" + key + EPClsPostfix.DST)
            if iface is not NULL_INTERFACE:
                jcg[key] = iface.to_json(json_c_graph=json_c_graph)
        return jcg

    def connect_all(self, fixed_interface: bool = True) -> None:
        """Connect all the unconnected destination endpoints in the Connection Graph."""
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
            vifs = (
                getattr(self, "_" + row + EPClsPostfix.SRC) for row in vsrc_rows[DstRow(dep.row)]
            )
            # Gather all the source endpoints that match the type of the destination endpoint.
            vsrcs = [sep for vif in vifs for sep in vif if sep.typ == dep.typ]
            # If the interface of the GC is not fixed (i.e. it is not an empty GC) then
            # a new input interface endpoint is an option.
            len_is = len(i_iface)
            if not fixed_interface:
                vsrcs.append(EndPoint(SrcRow.I, len_is, EndPointClass.SRC, dep.typ, []))
            if vsrcs:
                # Randomly choose a valid source endpoint
                sep: EndPoint = choice(vsrcs)
                # If it is a new input interface endpoint then add it to input interface
                if not fixed_interface and sep.idx == len_is and sep.row == SrcRow.I:
                    assert isinstance(i_iface.endpoints, list), "Input interface must be a list"
                    i_iface.endpoints.append(sep)
                # Connect the destination endpoint to the source endpoint
                dep.connect(sep)

    def copy(self) -> CGraph:
        """Return a modifiable shallow copy of the Connection Graph."""
        # Create a new CGraph instance with the same interfaces
        return CGraph({key[1:]: getattr(self, key) for key in _UNDER_ROW_CLS_INDEXED})

    def stabilize(self, fixed_interface: bool = True) -> None:
        """Stablization involves making all the mandatory connections and
        connecting all the remaining unconnected destination endpoints.
        Destinations are connected to sources in a random order.
        Stabilization is not guaranteed to be successful.
        """
