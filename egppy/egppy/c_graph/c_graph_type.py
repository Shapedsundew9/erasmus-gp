"""This module is used to determine the type of connection graph."""

from egpcommon.properties import CGraphType
from egppy.c_graph.c_graph_constants import DstRow, JSONCGraph
from egppy.c_graph.c_graph_abc import CGraphABC


def c_graph_type(jcg: JSONCGraph | CGraphABC) -> CGraphType:
    """Identify the connection graph type from the JSON graph."""
    assert DstRow.O in jcg, "All connection graphs must have a row O."
    assert DstRow.U in jcg or isinstance(
        jcg, CGraphABC
    ), "All JSON connection graphs must have a row U."
    if DstRow.F in jcg:
        assert DstRow.A in jcg, "All conditional connection graphs must have a row A."
        assert DstRow.P in jcg, "All conditional connection graphs must have a row P."
        return CGraphType.IF_THEN_ELSE if DstRow.B in jcg else CGraphType.IF_THEN
    if DstRow.L in jcg:
        assert DstRow.A in jcg, "All loop connection graphs must have a row A."
        assert DstRow.P in jcg, "All loop connection graphs must have a row P."
        return CGraphType.WHILE_LOOP if DstRow.W in jcg else CGraphType.FOR_LOOP
    if DstRow.B in jcg:
        assert DstRow.A in jcg, "A standard graph must have a row A."
        return CGraphType.STANDARD
    return CGraphType.PRIMITIVE if DstRow.A in jcg else CGraphType.EMPTY
