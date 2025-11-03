"""Code connection module."""

from __future__ import annotations

from collections.abc import Hashable
from typing import TYPE_CHECKING

from egpcommon.common import NULL_STR
from egppy.genetic_code.c_graph_constants import DstRow, EPClsPostfix, Row, SrcRow

if TYPE_CHECKING:
    from egppy.worker.executor.gc_node import GCNode


class CodeEndPoint(Hashable):
    """An code end point in the GC node graph."""

    __slots__ = ("node", "row", "idx", "terminal")

    def __init__(self, node: GCNode, row: Row, idx: int, terminal: bool = False) -> None:
        """Create a code end point in the GC node graph.

        When a code endpoint is terminal it defines where local variable is defined or used
        in the GC function executable implementation. If not terminal the code end point marks
        the most recently defined end of a code connection that is still being 'theaded' through
        the GC node graph.

        Args:
            node (GCNode): The node in the GC node graph.
            row (Row): The row in the node.
            idx (int): The index of the end point in the row.
            terminal (bool, optional): True if the end point is terminal. Defaults to False.
        """
        self.node: GCNode = node
        self.row: Row = row
        self.idx: int = idx
        self.terminal: bool = terminal

    def __eq__(self, other: object) -> bool:
        """Check equality of CodeEndPoint instances."""
        if not isinstance(other, CodeEndPoint):
            return NotImplemented
        return self.key() == other.key()

    def __hash__(self) -> int:
        """Return the hash of the CodeEndPoint instance."""
        return hash(self.key())

    def __repr__(self) -> str:
        """Return the representation of the CodeEndPoint instance."""
        return (
            f"CodeEndPoint({self.node.uid}(0x{self.node.gc['signature'].hex()[-8:]}), "
            f"{self.row}, {self.idx}, {self.terminal})"
        )

    def key(self) -> tuple:
        """Return the key for the CodeEndPoint instance."""
        return (self.node, self.row, self.idx, self.terminal)


class CodeConnection(Hashable):
    """A connection between terminal end points in the GC node graph."""

    __slots__ = ("src", "dst", "var_name")

    def __init__(self, src: CodeEndPoint, dst: CodeEndPoint) -> None:
        """Create a connection between code end points in the GC node graph."""
        self.src: CodeEndPoint = src
        self.dst: CodeEndPoint = dst
        self.var_name: str = NULL_STR

    def __eq__(self, other: object) -> bool:
        """Check equality of CodeConnection instances."""
        if not isinstance(other, CodeConnection):
            return NotImplemented
        return self.key() == other.key()

    def __hash__(self) -> int:
        """Return the hash of the CodeConnection instance."""
        return hash(self.key())

    def __repr__(self) -> str:
        """Return the representation of the CodeConnection instance."""
        return (
            f"CodeConnection({self.src.node.uid}(0x{self.src.node.gc['signature'].hex()[-8:]}), "
            f"{self.src.row}, {self.src.idx}, "
            f"{self.dst.node.uid}(0x{self.dst.node.gc['signature'].hex()[-8:]}), "
            f"{self.dst.row}, {self.dst.idx}, {self.var_name})"
        )

    def key(self) -> tuple:
        """Return the key for the CodeConnection instance."""
        return (self.src, self.dst, self.var_name)


def code_connection_from_iface(node: GCNode, row: Row) -> list[CodeConnection]:
    """Create a list of code connections from the interface of a node."""

    # Map the destination row in the node to the row in the destination node
    match row:
        case DstRow.A:
            dst_node = node.gca_node
            dst_row = SrcRow.I
        case DstRow.B:
            dst_node = node.gcb_node
            dst_row = SrcRow.I
        case _:
            dst_node = node
            dst_row = DstRow.O

    # Get the interface for this row
    iface = node.gc["cgraph"][row + EPClsPostfix.DST]
    result = []

    # Iterate through endpoints and their connections
    for ep in iface:
        conns = iface.get_connections(ep.idx)
        for conn in conns:
            # Create code connection from source to destination
            result.append(
                CodeConnection(
                    CodeEndPoint(node, conn.src_row, conn.src_idx),
                    CodeEndPoint(dst_node, dst_row, ep.idx, True),
                )
            )

    return result
