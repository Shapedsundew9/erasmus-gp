"""This module is used to determine the type of connection graph."""

from egpcommon.properties import CGraphType
from egppy.c_graph.c_graph_constants import DstRow, SrcRow


def c_graph_type(jcg: dict[DstRow, list[list[SrcRow | int | str]]]) -> CGraphType:
    """Identify the connection graph type from the JSON graph."""
    assert DstRow.O in jcg, "All connection graphs must have a row O."
    assert DstRow.U in jcg, "All JSON connection graphs must have a row U."
    if DstRow.F in jcg:
        assert DstRow.A in jcg, "All conditional connection graphs must have a row A."
        assert DstRow.P in jcg, "All conditional connection graphs must have a row P."
        return CGraphType.IF_THEN_ELSE if DstRow.B in jcg else CGraphType.IF_THEN
    if DstRow.L in jcg:
        assert DstRow.A in jcg, "All loop connection graphs must have a row A."
        assert DstRow.P in jcg, "All loop connection graphs must have a row P."
        return CGraphType.WHILE_LOOP if DstRow.W in jcg else CGraphType.FOR_LOOP
    assert (DstRow.A in jcg and DstRow.B in jcg) or (
        len(jcg) == 2 and DstRow.U in jcg
    ), "Connection graph is neither STANDARD nor EMPTY."
    return CGraphType.STANDARD if DstRow.A in jcg else CGraphType.EMPTY