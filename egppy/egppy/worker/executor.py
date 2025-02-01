"""The Executor Module.

The classes and functions in this module support the execution of Genetic Codes.
See [The Genetic Code Executor](docs/executor.md) for more information.
"""

from __future__ import annotations
from itertools import count
from egppy.gc_graph.typing import DestinationRow
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.typing import SourceRow, Row
from egppy.gc_types.gc import (
    GCABC,
    NULL_GC,
    NULL_EXECUTABLE,
    mc_circle_str,
    mc_connect_str,
    mc_rectangle_str,
    MERMAID_CODON_COLOR,
    MERMAID_GC_COLOR,
    MERMAID_UNKNOWN_COLOR,
    MERMAID_FOOTER,
    MERMAID_HEADER,
)
from egppy.worker.gc_store import GGC_CACHE


# Mermaid Chart creation helper function
def mc_gc_node_str(gcnode: GCNode, color: str = "") -> str:
    """Return a Mermaid Chart string representation of the GCNode in the logical structure.
    By default a blue rectangle is used for a GC unless it is a codon which is a green circle.
    If a color is specified then that color rectangle is used.
    """
    if color == "":
        color = MERMAID_GC_COLOR
        if gcnode.gc["num_codons"] == 1:
            return mc_codon_node_str(gcnode)
    label = f'"{gcnode.gc.signature().hex()[-8:]}<br>{gcnode.num_lines} lines"'
    return mc_rectangle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_unknown_node_str(gcnode: GCNode, color: str = MERMAID_UNKNOWN_COLOR) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc.signature().hex()[-8:]}<br>{gcnode.num_lines} lines"'
    return mc_circle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_codon_node_str(gcnode: GCNode, color: str = MERMAID_CODON_COLOR) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc.signature().hex()[-8:]}<br>{gcnode.num_lines} lines"'
    return mc_circle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_connection_node_str(gcnodea: GCNode, gcnodeb: GCNode) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return mc_connect_str(gcnodea.uid, gcnodeb.uid)


class GCNode:
    """A node in the GC Graph."""

    # For generating UIDs for GCNode instances
    _counter = count()

    def __init__(self, gc: GCABC, parent: GCNode | None):
        self.gc: GCABC = gc  # GCABC instance for this work dictionary
        if gc is not NULL_GC:
            # It is inefficient to pull the GC's that were not present in the cache (i.e.
            # are not GCABC objects) into the cache here as they may already have an executable
            # and be unchanging. The solution is to check for an executable here,
            # set GCA & GCB to NULL_GC and treat like the GC like a codon.
            gca: GCABC | bytes = gc["gca"]
            gcb: GCABC | bytes = gc["gcb"]
            # True if the function already exists
            self.exists: bool = gc["executable"] is not NULL_EXECUTABLE
            if not self.exists:
                # The GC may have an unknown structure but there is no existing executable
                # Need to pull the GC sub-GC's into cache to assess it
                if isinstance(gca, bytes):
                    gca = GGC_CACHE[gca]
                if isinstance(gcb, bytes):
                    gcb = GGC_CACHE[gcb]
            self.gca: GCABC = gca if isinstance(gca, GCABC) else NULL_GC
            self.gcb: GCABC = gcb if isinstance(gcb, GCABC) else NULL_GC
            self.iam: DestinationRow = DestinationRow.A  # The row this GC is in the parent
            # The parent work dictionary i.e. the GC that called this GC
            self.parent: GCNode = parent if parent is not None else NULL_GC_NODE
            self.assess: bool = True  # True if the number of lines has not been determined
            # True if ready to be written
            self.write: bool = False
            # Mark if the GC is unknown i.e. not in the cache
            self.unknown: bool = (self.gca is NULL_GC or self.gcb is NULL_GC) and gc[
                "num_codons"
            ] > 1
            # or self.exists: True if connections cannot thread through
            self.terminal: bool = self.write
            self.num_lines: int = gc["num_lines"] if self.exists else 0
            # Set to True if the GC is conditional and row F needs a connection
            self.f_connection = False
            # Will be defined if gca/b is not NULL_GC referring to a work dictionary
            self.gca_node: GCNode = NULL_GC_NODE
            self.gcb_node: GCNode = NULL_GC_NODE
            # Uniquely identify the node in the graph
            self.uid = f"uid{next(self._counter):04x}"

    def mermaid_chart(self) -> str:
        """Return the Mermaid chart for the GC node graph."""
        return "\n".join(MERMAID_HEADER + self._mermaid_body(self) + MERMAID_FOOTER)

    def _mermaid_body(self, gc_node: GCNode) -> list[str]:
        """Return the Mermaid chart for the GC node graph."""
        # If the GC executable exists then return a green node
        if gc_node.exists:
            return [mc_gc_node_str(gc_node, "green")]

        # Build up the GC structure chart
        work_queue: list[tuple[GCNode, GCNode, GCNode]] = [
            (gc_node, gc_node.gca_node, gc_node.gcb_node)
        ]
        chart_txt: list[str] = [mc_gc_node_str(gc_node)]
        while work_queue:
            gc_node, gca_node, gcb_node = work_queue.pop(0)
            if gca_node is not NULL_GC_NODE:
                if gca_node.exists or gca_node.write:
                    chart_txt.append(f'    subgraph {gca_node.uid}sd[" "]')
                    chart_txt.extend(self._mermaid_body(gca_node))
                    chart_txt.append("    end")
                    chart_txt.append(mc_connection_node_str(gc_node, gca_node))
                elif not gca_node.unknown:
                    work_queue.append((gca_node, gca_node.gca_node, gca_node.gcb_node))
                    chart_txt.append(mc_gc_node_str(gca_node))
                    chart_txt.append(mc_connection_node_str(gc_node, gca_node))
                else:
                    chart_txt.append(mc_unknown_node_str(gca_node))
                    chart_txt.append(mc_connection_node_str(gc_node, gca_node))
            if gcb_node is not NULL_GC_NODE:
                if gcb_node.exists or gcb_node.write:
                    chart_txt.append(f'    subgraph {gcb_node.uid}sd[" "]')
                    chart_txt.extend(self._mermaid_body(gcb_node))
                    chart_txt.append("    end")
                    chart_txt.append(mc_connection_node_str(gc_node, gcb_node))
                elif not gcb_node.unknown:
                    work_queue.append((gcb_node, gcb_node.gca_node, gcb_node.gcb_node))
                    chart_txt.append(mc_gc_node_str(gcb_node))
                    chart_txt.append(mc_connection_node_str(gc_node, gcb_node))
                else:
                    chart_txt.append(mc_unknown_node_str(gcb_node))
                    chart_txt.append(mc_connection_node_str(gc_node, gcb_node))
        return chart_txt


# The null GC node is used to indicate that a GC does not exist. It is therefore not a leaf node but
# if bot GCA and GCB are NULL_GC_NODE then it is a leaf node.
NULL_GC_NODE = GCNode(NULL_GC, None)


def node_graph(gc: GCABC, limit: int) -> GCNode:
    """Build the bi-directional graph of GC's.

    The graph is a graph of GCNode objects. A GCNode object for a GC references nodes
    for each of its GCA & GCB if they exist. Note that the graph is a representation
    of the GC implementation and so each node is an instance of a GC not a definition.
    i.e. the same GC may appear multiple times in the graph. This matters because each instance
    may be implemented differently depending on what other GC's are local to it in the GC structure
    graph.

    Args:
        gc (GCABC): Is the root of the graph.
        limit (int): The maximum number of lines per function

    Returns:
        GCNode: The graph root node.
    """
    assert (
        2 <= limit <= 2**15 - 1
    ), f"Invalid function maximum lines limit: {limit} must be 2 <= limit <= 32767"

    half_limit: int = limit // 2
    node_stack: list[GCNode] = [gc_node_graph := GCNode(gc, None)]

    # Define the GCNode data
    while node_stack:
        # See [Assessing a GC for Function Creation](docs/executor.md) for more information.
        node: GCNode = node_stack.pop(0)
        for row, xgc in (x for x in (("A", node.gca), ("B", node.gcb)) if x[1] is not NULL_GC):
            gc_node_graph_entry: GCNode = GCNode(xgc, node)
            node.f_connection = xgc["graph"].is_conditional_graph()
            if row == "A":
                node.gca_node = gc_node_graph_entry
                gc_node_graph_entry.iam = DestinationRow.A
            else:
                node.gcb_node = gc_node_graph_entry
                gc_node_graph_entry.iam = DestinationRow.B
            lines = xgc["num_lines"]
            assert lines <= limit, f"Number of lines in function exceeds limit: {lines} > {limit}"
            if xgc["executable"] is not NULL_EXECUTABLE:
                assert lines > 0, f"The # lines cannot be <= 0 when there is an executable: {lines}"
                if lines < half_limit:
                    node_stack.append(gc_node_graph_entry)
                else:
                    # Existing executable is suitable (so no need to assess or write it)
                    gc_node_graph_entry.assess = False
                    gc_node_graph_entry.exists = True
                    gc_node_graph_entry.terminal = True
                    gc_node_graph_entry.num_lines = lines
            else:
                node_stack.append(gc_node_graph_entry)
        if node.gca is NULL_GC and node.gcb is NULL_GC:
            # This is a leaf GC i.e. a codon
            node.num_lines = 1
            node.assess = False
    return gc_node_graph


def line_count(gc_node_graph: GCNode, limit: int) -> None:
    """Calculate the best number of lines for each function and
    mark the ones that should be written. This function traverses the graph
    starting at the root and working down to the leaves (codons) and then
    back up to the root accumulating line counts.

    When a node that meets the criteria to be written is found then the node is marked
    as to be written, terminal and the line count is set. The node is then marked as
    no longer needing assessment.
    """
    node: GCNode = gc_node_graph
    while node.assess:

        # If GCA exists and needs assessing then assess it
        gca_node: GCNode = node.gca_node
        if gca_node.assess:
            node = gca_node
            continue

        # If GCB exists and needs assessing then assess it
        num_lines_gca: int = gca_node.num_lines
        if node.gcb_node is not NULL_GC_NODE:
            gcb_node: GCNode = node.gcb_node
            if gcb_node.assess:
                node = gcb_node
                continue

            # If both GCA & GCB have been assessed then determine the best number of lines
            # and mark the one to be written (if it does not already exist)
            # Initialize the interface to the written function for threading connections later.
            num_lines_gcb: int = gcb_node.num_lines
            if num_lines_gca == num_lines_gcb == limit:
                gca_node.write = not gca_node.exists
                gca_node.terminal = True
                gcb_node.write = not gcb_node.exists
                gcb_node.terminal = True
                node.num_lines = 2
            elif num_lines_gca + num_lines_gcb > limit:
                bi_gcx: GCNode = gcb_node if num_lines_gca < num_lines_gcb else gca_node
                bi_gcx.write = not bi_gcx.exists
                bi_gcx.terminal = True
                node.num_lines = 1 + (num_lines_gcb if bi_gcx is gca_node else num_lines_gca)
            else:
                node.num_lines = num_lines_gca + num_lines_gcb
        else:
            node.num_lines = num_lines_gca

        # Mark the node as assessed and move to the parent
        # If the parent is empty then the bigraph line count is complete
        node.assess = False
        if node.parent is not NULL_GC_NODE:
            node = node.parent


class CodeEndPoint:
    """An code end point in the GC node graph."""

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


class CodeConnection:
    """A connection between terminal end points in the GC node graph."""

    def __init__(self, src: CodeEndPoint, dest: CodeEndPoint) -> None:
        """Create a connection between code end points in the GC node graph."""
        self.src: CodeEndPoint = src
        self.dest: CodeEndPoint = dest


def code_connection_from_iface(node: GCNode, row: Row) -> list[CodeConnection]:
    """Create a list of code connections from the interface of a node."""

    return [
        CodeConnection(
            CodeEndPoint(node, r[0].get_row(), r[0].get_idx()),
            CodeEndPoint(node, row, i, True),
        )
        for i, r in enumerate(node.gc["graph"][row + "dc"])
    ]


def code_graph(function: GCNode) -> list[CodeConnection]:
    """The inputs and outputs of each function are determined by the connections between GC's.
    This function traverses the function sub-graph and makes the connections between terminal
    nodes. Since only destination endpoints are required to be connected the connections are made
    from the destination to the source (this avoids writing out "dead code").

    1. Start at the top level GC (root of the function graph).
    2. Create code_connection objects for each output of the GC.
    3. Push them individually onto the work stack.
    4. Work through the stack until all connections are terminal.
        a. If a source code end point is not terminal find what it is connected to
           and push it onto the stack.
        b. If a destination code end point is not terminal find what it is connected to
           and push it onto the stack.


    """
    node: GCNode = function  # This is the root of the graph for the GC function to be written
    terminal_connections: list[CodeConnection] = []

    # If the GC is a codon then there are no connections to make
    if node.gca is NULL_GC and node.gcb is NULL_GC:
        return terminal_connections
    connection_stack: list[CodeConnection] = code_connection_from_iface(node, DestinationRow.O)

    # Work through the connections until they all have terminal sources and destinations
    while connection_stack:
        connection: CodeConnection = connection_stack[-1]
        src: CodeEndPoint = connection.src
        node: GCNode = src.node

        # If this node is conditional and so a connection to row F must be made
        if node.f_connection:
            node.f_connection = False
            connection_stack.append(
                CodeConnection(
                    CodeEndPoint(node, SourceRow.I, node.gc["graph"]["Fdc"][0].get_idx()),
                    CodeEndPoint(node, DestinationRow.F, 0, True),
                )
            )

        # If the source is not terminal then find what it is connected to
        if not src.terminal:
            match src.row:
                case SourceRow.A:
                    assert node.gca is not NULL_GC, "Should never introspect a codon graph."
                    src.node = node.gca_node
                    src.terminal = node.gca_node.terminal
                    refs = src.node.gc["graph"]["Odc"]
                case SourceRow.B:
                    assert node.gcb is not NULL_GC, "GCB cannot be NULL"
                    src.node = node.gcb_node
                    src.terminal = node.gcb_node.terminal
                    refs = src.node.gc["graph"]["Odc"]
                case SourceRow.I:
                    parent: GCNode = node.parent
                    if parent is not NULL_GC_NODE:
                        src.node = parent
                        src.terminal = parent.terminal
                        refs = src.node.gc["graph"][node.iam + "dc"]
                    else:
                        refs = []
                        src.terminal = True
                case _:
                    raise ValueError(f"Invalid source row: {src.row}")
            # In all none terminal cases the new source row and index populated from the
            # gc_graph connection.
            if not src.terminal:
                ref: XEndPointRefABC = refs[src.idx][0]
                src.row = ref.get_row()
                src.idx = ref.get_idx()
        else:
            # If the source is terminal then we are only done if the parent node does not exist
            # i.e. the root of the graph. If the parent node exists then we need to find the
            # input interface and make sure that is connected.
            # node.iam tells us which row defines the interface.
            parent: GCNode = node.parent
            if parent is not NULL_GC_NODE:
                connection_stack.extend(code_connection_from_iface(parent, node.iam))

        # Is this connection completed?
        if src.terminal:
            assert connection.dest.terminal, "Destination must be terminal."
            terminal_connections.append(connection)
            connection_stack.pop()

    # Return the list of connections between all terminal code endpoints
    return terminal_connections


def write_gc_executable(gc: GCABC | bytes, limit: int = 20) -> tuple[list[str], list[str]]:
    """Write the code for the GC.

    Sub-GC's are looked up in the gc_store.
    The returned lists are the imports and functions.
    Note that functions will be between limit/2 and limit lines long.

    1. Graph bi-directional graph of GC's

    Args:
        gc_store (CacheABC): The cache of GC's.
        gc (GCABC | bytes): The Genetic Code.
        limit (int, optional): The maximum number of lines per function. Defaults to 20.
    """
    sig: bytes = gc.signature() if isinstance(gc, GCABC) else gc
    assert isinstance(sig, bytes), f"Invalid signature type: {type(sig)}"
    _gc: GCABC = gc if isinstance(gc, GCABC) else GGC_CACHE[sig]

    # If the GC executable has already been written then return
    if _gc["executable"] is not NULL_EXECUTABLE:
        return [], []

    # The GC may have been assessed as part of another GC but not an executable in its own right
    # The GC node graph is needed to determine connectivity and so we reset the num_lines
    # and re-assess
    gc_node_graph: GCNode = node_graph(_gc, limit)
    line_count(gc_node_graph, limit)
    _: list[CodeConnection] = code_graph(gc_node_graph)

    return [], []
