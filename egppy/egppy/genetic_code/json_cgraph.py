"""JSON Connection Graph validation and conversion functions."""

from __future__ import annotations

from egpcommon.common import NULL_FROZENSET
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import (
    CPI,
    SOURCE_ROW_MAP,
    DstRow,
    EPCls,
    EPClsPostfix,
    JSONCGraph,
    Row,
    SrcRow,
)
from egppy.genetic_code.endpoint_abc import EndpointMemberType
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
# This pattern involves creating a logger instance using the egp_logger function,
# and setting up boolean flags to check if certain logging levels (DEBUG, VERIFY, CONSISTENCY)
# are enabled. This allows for conditional logging based on the configured log level.
_logger: Logger = egp_logger(name=__name__)


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

    The JSON connection graph format is as follows:
    {
        "DstRow1": [ [src_row: str, src_idx: int, endpoint_type: str], ... ],
        "DstRow2": [ [src_row: str, src_idx: int, endpoint_type: str], ... ],
        ...
    }
    DstRowX is a string representing the destination row (e.g., "A", "O", etc.).
    and must be in the order defined in DstRow enum.
    DstRowX key:value pairs must only be present if at least one source endpoint
    is defined.
    The rules defining connection graphs are such that the existence of an interface
    can be inferred. See c_graph_abc.py module docstring for more details.

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
        for src in jcg.get(dst, []):
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


def json_cgraph_to_interfaces(jcg: JSONCGraph) -> dict[str, list[EndpointMemberType]]:
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
    src_ep_dict: dict[SrcRow, dict[int, EndpointMemberType]] = {}

    # Create destination interfaces from JSON structure
    interfaces: dict[str, list[EndpointMemberType]] = {}

    # Process each destination row in the JSON graph
    for dst_row, idef in jcg.items():
        # Create destination interface
        dst_iface_key = dst_row + EPClsPostfix.DST
        dst_interface: list[EndpointMemberType] = [
            (DstRow(dst_row), i, EPCls.DST, types_def_store[v[2]], [[SrcRow(v[0]), v[1]]])
            for i, v in enumerate(idef)
        ]
        interfaces[dst_iface_key] = dst_interface

        # Build source endpoint references for each destination endpoint
        for ep in dst_interface:
            for ref in ep[4]:
                # Create source endpoints that correspond to destination references
                src_row = SrcRow(ref[0])
                src_idx = ref[1]

                src_ep_dict.setdefault(src_row, {})
                if src_idx in src_ep_dict[src_row]:
                    # Source endpoint already exists, validate type consistency and add reference
                    src_ep = src_ep_dict[src_row][src_idx]
                    if src_ep[3] != ep[3]:
                        raise ValueError(
                            f"Type inconsistency for source endpoint {src_row},{src_idx}: "
                            f"existing type '{src_ep[2].name}' "
                            f"conflicts with new type '{ep[3].name}'"
                        )
                    refs = src_ep[4]
                    assert isinstance(refs, list), "Expected refs to be a list."
                    refs.append([DstRow(dst_row), ep[1]])
                else:
                    # Create new source endpoint
                    assert isinstance(
                        src_idx, int
                    ), f"Expected an integer index, got {type(src_idx)}"
                    src_ep_dict[src_row][src_idx] = (
                        SrcRow(src_row),
                        src_idx,
                        EPCls.SRC,
                        ep[3],
                        [[DstRow(dst_row), ep[1]]],
                    )

    # Create source interfaces from the collected source endpoints
    for src_row, eps in src_ep_dict.items():
        src_iface_key = src_row + EPClsPostfix.SRC
        interfaces[src_iface_key] = sorted(eps.values(), key=lambda x: x[1])

    # Create missing interfaces with no endpoints
    if "Is" not in interfaces:
        interfaces["Is"] = []
    if "Ad" not in interfaces and "As" in interfaces:
        interfaces["Ad"] = []
    if "As" not in interfaces and "Ad" in interfaces:
        interfaces["As"] = []
    if "Bd" not in interfaces and "Bs" in interfaces:
        interfaces["Bd"] = []
    if "Bs" not in interfaces and "Bd" in interfaces:
        interfaces["Bs"] = []
    if "Od" not in interfaces:
        interfaces["Od"] = []
    if "Od" in interfaces and ("Fd" in interfaces or "Ld" in interfaces) and "Pd" not in interfaces:
        interfaces["Pd"] = []
    return interfaces


def c_graph_type(jcg: JSONCGraph | CGraphABC) -> CGraphType:
    """Identify the connection graph type from the JSON graph."""
    # Find all the rows present in the connection graph
    # For a JSONCGraph it is necessarily to introspect all the destination
    # endpoints to find the source rows as well as ensure I and O are included.
    if isinstance(jcg, dict):
        jcg_set = set(jcg) | {src[0] for row in jcg.values() for src in row} | {"O", "I"}
        if "F" in jcg_set or "L" in jcg_set or "W" in jcg_set:
            # Ensure P exists if F, L, or W exist (it will not as it is always a duplicate of Od)
            jcg_set.add("P")
    else:
        jcg_set = set(k[0] for k in jcg)
    if _logger.isEnabledFor(level=DEBUG):
        if DstRow.O not in jcg_set:
            raise ValueError("All connection graphs must have a row O.")
        if DstRow.F in jcg_set:
            if DstRow.A not in jcg_set:
                raise ValueError("All conditional connection graphs must have a row A.")
            if DstRow.P not in jcg_set:
                raise ValueError("All conditional connection graphs must have a row P.")
            return CGraphType.IF_THEN_ELSE if DstRow.B in jcg_set else CGraphType.IF_THEN
        if DstRow.L in jcg_set:
            if DstRow.A not in jcg_set:
                raise ValueError("All loop connection graphs must have a row A.")
            if DstRow.P not in jcg_set:
                raise ValueError("All loop connection graphs must have a row P.")
            return CGraphType.WHILE_LOOP if DstRow.W in jcg_set else CGraphType.FOR_LOOP
        if DstRow.B in jcg_set:
            if DstRow.A not in jcg_set:
                raise ValueError("A standard graph must have a row A.")
            return CGraphType.STANDARD

    # Same as above but without the checks
    if DstRow.F in jcg_set:
        return CGraphType.IF_THEN_ELSE if DstRow.B in jcg_set else CGraphType.IF_THEN
    if DstRow.L in jcg_set:
        return CGraphType.WHILE_LOOP if DstRow.W in jcg_set else CGraphType.FOR_LOOP
    if DstRow.B in jcg_set:
        return CGraphType.STANDARD
    return CGraphType.PRIMITIVE if DstRow.A in jcg_set else CGraphType.EMPTY
