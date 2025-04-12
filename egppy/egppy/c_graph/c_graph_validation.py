"""The connection Graph Validation module.

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
"""

from egpcommon.properties import CGraphType
from egpcommon.common import NULL_FROZENSET
from egppy.c_graph.c_graph_constants import DstRow, SrcRow, CPI
from egppy.c_graph.c_graph_type import c_graph_type

# NOTE: There are a lot of duplicate frozensets in this module. They have not been reduced to
# constants because they are used in different contexts and it is not clear that they
# can be safely reused as they are in different contexts (and future changes may then
# propagate inappropriately).


def valid_src_rows(graph_type: CGraphType, u=False) -> dict[DstRow, frozenset[SrcRow]]:
    """Return a dictionary of valid source rows for the given graph type.

    NOTE: Row U is only needed for JSON format connection graphs.

    Args:
        graph_type: The type of graph to validate.
        u: If True, include the Ud row in the result.
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
                DstRow.L: frozenset(SrcRow.I),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.P: frozenset(SrcRow.I),
            }
        case CGraphType.WHILE_LOOP:
            retval = {
                DstRow.A: frozenset({SrcRow.I, SrcRow.L}),
                DstRow.L: frozenset(SrcRow.I),
                DstRow.W: frozenset(SrcRow.A),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.P: frozenset(SrcRow.I),
            }
        case CGraphType.STANDARD:
            retval = {
                DstRow.A: frozenset(
                    {
                        SrcRow.I,
                    }
                ),
                DstRow.B: frozenset({SrcRow.I, SrcRow.A}),
                DstRow.O: frozenset({SrcRow.I, SrcRow.A, SrcRow.B}),
            }
        case _:
            raise ValueError(f"Invalid graph type: {graph_type}")

    if u:
        # Add the U row to the dictionary
        # U row is a special case, it can be connected to any source row
        if graph_type == CGraphType.EMPTY:
            retval[DstRow.U] = frozenset(
                SrcRow.I,
            )
        else:
            retval[DstRow.U] = frozenset(
                {src for srcs in retval.values() for src in srcs} | retval[DstRow.U]
            )
    return retval


def valid_dst_rows(graph_type: CGraphType) -> dict[SrcRow, frozenset[DstRow]]:
    """Return a dictionary of valid destination rows for the given graph type."""
    match graph_type:
        case CGraphType.IF_THEN:
            return {
                SrcRow.I: frozenset(
                    {
                        DstRow.A,
                        DstRow.F,
                        DstRow.O,
                        DstRow.P,
                    }
                ),
                SrcRow.A: frozenset((DstRow.O,)),
            }
        case CGraphType.IF_THEN_ELSE:
            return {
                SrcRow.I: frozenset(
                    {
                        DstRow.A,
                        DstRow.F,
                        DstRow.B,
                        DstRow.P,
                        DstRow.O,
                    }
                ),
                SrcRow.A: frozenset({DstRow.O}),
                SrcRow.B: frozenset({DstRow.P}),
            }
        case CGraphType.EMPTY:
            return {
                SrcRow.I: NULL_FROZENSET,
            }
        case CGraphType.FOR_LOOP:
            return {
                SrcRow.I: frozenset(
                    {
                        DstRow.A,
                        DstRow.L,
                        DstRow.O,
                        DstRow.P,
                    }
                ),
                SrcRow.L: frozenset({DstRow.A}),
                SrcRow.A: frozenset({DstRow.O}),
            }
        case CGraphType.WHILE_LOOP:
            return {
                SrcRow.I: frozenset(
                    {
                        DstRow.A,
                        DstRow.L,
                        DstRow.O,
                        DstRow.P,
                    }
                ),
                SrcRow.L: frozenset({DstRow.A}),
                SrcRow.A: frozenset({DstRow.O, DstRow.W}),
            }
        case CGraphType.STANDARD:
            return {
                SrcRow.I: frozenset(
                    {
                        DstRow.A,
                        DstRow.B,
                        DstRow.O,
                    }
                ),
                SrcRow.A: frozenset({DstRow.B, DstRow.O}),
                SrcRow.B: frozenset({DstRow.O}),
            }
        case _:
            raise ValueError(f"Invalid graph type: {graph_type}")


def valid_jcg(jcg: dict[DstRow, list[list[SrcRow | int | str]]]) -> bool:
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
    for key, value in jcg.items():
        if not isinstance(value, list):
            raise ValueError(f"Invalid value in JSON connection graph: {value}")
        for item in value:
            if not isinstance(item, (SrcRow, int, str)):
                raise ValueError(f"Invalid item in JSON connection graph: {item}")

    # Check that connectivity is valid
    for dst, vsr in valid_src_rows(c_graph_type(jcg)).items():
        if dst not in jcg:
            raise ValueError(f"Missing destination row in JSON connection graph: {dst}")
        for src in jcg[dst]:
            assert isinstance(src[CPI.ROW], SrcRow), "Expected a source row"
            row = src[CPI.ROW]
            idx = src[CPI.IDX]
            ept = src[CPI.TYP]
            assert isinstance(row, SrcRow), "Expected a source row"
            assert isinstance(idx, int), "Expected an integer index"
            assert isinstance(ept, str), "Expected a string endpoint type"
            if row not in vsr:
                raise ValueError(
                    f"Invalid source row in JSON connection graph: {row} for destination {dst}"
                )
            if not 0 < idx < 256:
                raise ValueError(
                    f"Index out of range for JSON connection graph: {idx} for destination {dst}"
                )

    return True
