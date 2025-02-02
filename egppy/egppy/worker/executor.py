"""The Executor Module.

The classes and functions in this module support the execution of Genetic Codes.
See [The Genetic Code Executor](docs/executor.md) for more information.
"""

from __future__ import annotations
from typing import Any
from itertools import count
from collections.abc import Hashable, Iterable, Iterator
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


# Code string templates
def gc_function_call_cstr(gcnode: GCNode) -> str:
    """Return the code string for the GC function call."""
    assert gcnode.global_index >= 0, "Global index must be >= 0"
    return f"f_{gcnode.global_index:08x}(i)"


def gc_inline_cstr(gcnode: GCNode) -> str:
    """Return the code string for the GC inline code."""
    # TODO: Need to add parameter elabotation here
    return gcnode.gc["inline"]


def i_cstr(n: int) -> str:
    """Return the code string for the nth input.
    GC inputs are always implemented as a tuple named 'i'.
    The number of inputs is limited to 256 in a GC.
    """
    assert 0 <= n <= 255, f"Invalid input index: {n} must be 0 <= n <= 255"
    return f"i[{n:03d}]"


def o_cstr(n: int) -> str:
    """Return the code string for the nth output variable.
    Output variables are assigned to.
    The number of outputs in a GC is limited to 256.
    """
    assert 0 <= n <= 255, f"Invalid output index: {n} must be 0 <= n <= 255"
    return f"o{n:03d}"


def t_cstr(n: int) -> str:
    """Return the code string for the nth temporary variable.
    Temporary variables are assigned to.
    The number of temporary variables in a function is limited to 100,000.
    """
    assert 0 <= n <= 99999, f"Invalid temporary index: {n} must be 0 <= n <= 99999"
    return f"t{n:05d}"


# Mermaid Chart creation helper function
def mc_gc_node_str(gcnode: GCNode, row: Row, color: str = "") -> str:
    """Return a Mermaid Chart string representation of the GCNode in the logical structure.
    By default a blue rectangle is used for a GC unless it is a codon which is a green circle.
    If a color is specified then that color rectangle is used.
    """
    if color == "":
        color = MERMAID_GC_COLOR
        if gcnode.gc["num_codons"] == 1:
            return mc_codon_node_str(gcnode, row)
    label = f'"{gcnode.gc.signature().hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_rectangle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_unknown_node_str(gcnode: GCNode, row: Row, color: str = MERMAID_UNKNOWN_COLOR) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc.signature().hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_circle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_codon_node_str(gcnode: GCNode, row: Row, color: str = MERMAID_CODON_COLOR) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc.signature().hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_circle_str(gcnode.uid, label, color)


def mc_code_node_str(gcnode: GCNode) -> str:
    """Return a Mermaid Chart string representation of the code (terminal GCNode)."""
    if gcnode.exists or gcnode.write:
        label = f"{gc_function_call_cstr(gcnode)}<br>{gcnode.gc['signature'].hex()[-8:]}"
        return mc_rectangle_str(gcnode.uid, label, "green")
    assert (
        gcnode.gc.is_codon()
    ), "If the GC function does not exist and is not going to, it must be a codon."
    label = f"{gcnode.gc["inline"]}<br>{gcnode.gc['signature'].hex()[-8:]}"
    return mc_circle_str(gcnode.uid, label, "green")


# Mermaid Chart creation helper function
def mc_connection_node_str(gcnodea: GCNode, gcnodeb: GCNode) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return mc_connect_str(gcnodea.uid, gcnodeb.uid)


class ExecutionContext:
    """An execution context is a virtual python namespace where GC functions are defined.
    Some additional information is also stored in the context to keep track of global
    variable indices etc.

    The intent of an execution context is to encapsulate the code execution process
    so that multiple instances of the executor can be run concurrently without
    interfering with each other and every bit of related data created within in it
    can be garbage collected at the top level by standard mechanisms when it is
    destroyed. This is important because GC's are able to create new GC's and
    persistent data structures that are not easy to track.
    """

    def __init__(self) -> None:
        self.namespace: dict[str, Any] = {}
        # Used to uniquely name objects in this context
        self.global_index = count()

    def define(self, code: str) -> None:
        """Define a function in the execution context."""
        exec(code, self.namespace)  # pylint: disable=exec-used

    def destroy(self, objects: Iterable[str]) -> None:
        """Destroy objects in the execution context."""
        for obj in (o for o in objects if o in self.namespace):
            del self.namespace[obj]


class GCNodeIterator(Iterator):
    """An iterator for the entire GCNode graph."""

    def __init__(self, root) -> None:
        """Create an iterator for the GCNode graph.
        Start the iterator at the 1st codon on the execution path.
        """
        self._visted: set[GCNode] = set()
        if root is NULL_GC_NODE:
            self.stack: list[GCNode] = []
        else:
            # Explore to the furthest GCA terminal node in the graph
            # This is the first node on the execution path
            self.stack: list[GCNode] = [root]
            self._traverse(root)

    def __next__(self) -> GCNode:
        if not self.stack:
            raise StopIteration

        node: GCNode = self.stack[-1]

        # The GCA path of the graph has been explored to the end
        # If this node has a GCB it must be explored down its
        # GCA path to its furthest limit as this is the next
        # terminal node in the graph.
        if node.gcb_node is not NULL_GC_NODE and node.gcb_node not in self._visted:
            node = node.gcb_node
            self._visted.add(node)
            self.stack.append(node)
            self._traverse(node)
        return self.stack.pop()

    def _traverse(self, node: GCNode) -> None:
        """Traverse the GCNode graph to the limit of the GCA nodes."""
        while node.gca_node is not NULL_GC_NODE:
            node = node.gca_node
            self.stack.append(node)


class GCNodeCodeIterator(Iterator):
    """An iterator for only inline nodes of the graph.
    i.e. nodes that have been or will be written as functions
    are not iterated deeper than the root node.
    """

    def __init__(self, root) -> None:
        """Create an iterator for the GCNode graph.
        Start the iterator at the 1st codon on the execution path.
        """
        self._visted: set[GCNode] = set()
        if root is NULL_GC_NODE:
            self.stack: list[GCNode] = []
        else:
            # Explore to the furthest GCA terminal node in the graph
            # This is the first node on the execution path
            self.stack: list[GCNode] = [root]
            self._traverse(root)

    def __next__(self) -> GCNode:
        if not self.stack:
            raise StopIteration

        node: GCNode = self.stack[-1]

        # The GCA path of the graph has been explored to the end
        # If this node has a GCB it must be explored down its
        # GCA path to its furthest limit as this is the next
        # terminal node in the graph.
        if node.gcb_node is not NULL_GC_NODE and node.gcb_node not in self._visted:
            node = node.gcb_node
            self._visted.add(node)
            self.stack.append(node)
            self._traverse(node)
        return self.stack.pop()

    def _traverse(self, parent: GCNode) -> None:
        """Traverse the GCNode graph to the limit of the GCA nodes."""
        node = parent.gca_node
        while not (parent.write or parent.exists) and (node is not NULL_GC_NODE):
            parent = node
            self.stack.append(node)
            node = node.gca_node


class GCNodeCodeIterable(Iterable):
    """An iterable for only inline nodes of the graph."""

    def __init__(self, root) -> None:
        self.root = root

    def __iter__(self) -> Iterator[GCNode]:
        return GCNodeCodeIterator(self.root)


class GCNode(Iterable, Hashable):
    """A node in the GC Graph."""

    # For generating UIDs for GCNode instances
    _counter = count()

    def __init__(self, ec: ExecutionContext, gc: GCABC, parent: GCNode | None) -> None:
        self.ec: ExecutionContext = ec  # The execution context for this work dictionary
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
            self.iam: Row = SourceRow.I  # The row this GC is in the parent
            # The parent work dictionary i.e. the GC that called this GC
            self.parent: GCNode = parent if parent is not None else NULL_GC_NODE
            self.assess: bool = True  # True if the number of lines has not been determined
            # True if ready to be written (only functions are written)
            self.write: bool = False
            # Mark if the GC is unknown i.e. not in the cache
            self.unknown: bool = (self.gca is NULL_GC or self.gcb is NULL_GC) and not gc.is_codon()
            # or self.exists: True if connections cannot thread through
            self.terminal: bool = self.write or gc.is_codon()
            self.num_lines: int = gc["num_lines"] if self.exists else 0
            # Set to True if the GC is conditional and row F needs a connection
            self.f_connection = False
            # Will be defined if gca/b is not NULL_GC referring to a work dictionary
            self.gca_node: GCNode = NULL_GC_NODE
            self.gcb_node: GCNode = NULL_GC_NODE
            # Uniquely identify the node in the graph
            self.uid = f"uid{next(self._counter):04x}"
            # The code connection end points if this node is to be written
            self.terminal_connections: list[CodeConnection] = []
            # Node to be written need a unique global index in the execution context
            # Valid indices are >= 0. If the executabel exists then the global index is set
            # and can be retrieved from the executable name.
            self.global_index = int(self.gc["executable"].__name__[-8:], 16) if self.exists else -1

    def __hash__(self) -> int:
        """Return the hash of the GCNode instance."""
        return hash(self.uid)

    def __iter__(self) -> Iterator[GCNode]:
        """Return an iterator for the entire GCNode graph."""
        return GCNodeIterator(self)

    def __str__(self) -> str:
        """Return the representation of the GCNode instance."""
        str_list: list[str] = [f"GCNode root: {self.gc['signature'].hex()}"]
        for node in self:
            str_list.append(f"\tsignature: {node.gc['signature'].hex()}")
            for k, v in vars(node).items():
                if not isinstance(v, GCNode):
                    str_list.append(f"\t{k}: {v}")
                else:
                    str_list.append(f"\t{k}: {repr(v)}")
            str_list.append("\n")
        return "\n".join(str_list)

    def code_mermaid_chart(self) -> str:
        """Return the Mermaid chart for the GC code graph.
        In the event the node will not be written then return an empty string."""
        if not self.write:
            return ""
        title_txt: list[str] = [
            "---",
            f"title: \"{gc_function_call_cstr(self)}<br>{self.gc['signature'].hex()[-8:]}\"",
            "---",
        ]
        chart_txt: list[str] = []

        # Iterate through the node graph in depth-first order (A then B)
        for node in (tn for tn in GCNodeCodeIterable(self) if tn.terminal):
            chart_txt.append(mc_code_node_str(node))
        return "\n".join(title_txt + MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

    def create_code_graphs(self) -> list[GCNode]:
        """Return the list of GCNode instances that need to be written. i.e. that need code graphs.
        If a node (function) is not yet written it has not been assigned a global index.
        """
        print("Pre-node-write:\n", [gcng.gc["signature"].hex() for gcng in self if gcng.write])
        print(self)
        nwcg: list[GCNode] = [code_graph(gcng) for gcng in self if gcng.write]
        assert all(
            node.global_index == -1 for node in nwcg
        ), "Global index must not already be set."
        for node in nwcg:
            node.global_index = next(node.ec.global_index)
        assert all(
            all(c.src.terminal and c.dest.terminal for c in gcng.terminal_connections)
            for gcng in nwcg
        ), "All source connections endpoints must be terminal for a GC to be written."
        print(self)
        return nwcg

    def mermaid_chart(self) -> str:
        """Return the Mermaid chart for the GC node graph."""
        return "\n".join(MERMAID_HEADER + self._mermaid_body(self) + MERMAID_FOOTER)

    def _mermaid_body(self, gc_node: GCNode) -> list[str]:
        """Return the Mermaid chart for the GC node graph."""
        # If the GC executable exists then return a green node
        if gc_node.exists:
            return [mc_gc_node_str(gc_node, gc_node.iam, "green")]

        # Build up the GC structure chart
        work_queue: list[tuple[GCNode, GCNode, GCNode]] = [
            (gc_node, gc_node.gca_node, gc_node.gcb_node)
        ]
        chart_txt: list[str] = [mc_gc_node_str(gc_node, gc_node.iam)]
        while work_queue:
            gc_node, gca_node, gcb_node = work_queue.pop(0)
            for gcx_node, row in ((gca_node, SourceRow.A), (gcb_node, SourceRow.B)):
                if gcx_node is not NULL_GC_NODE:
                    if gcx_node.exists or gcx_node.write:
                        chart_txt.append(f'    subgraph {gcx_node.uid}sd[" "]')
                        chart_txt.extend(self._mermaid_body(gcx_node))
                        chart_txt.append("    end")
                        chart_txt.append(mc_connection_node_str(gc_node, gcx_node))
                    elif not gcb_node.unknown:
                        work_queue.append((gcx_node, gcx_node.gca_node, gcx_node.gcb_node))
                        chart_txt.append(mc_gc_node_str(gcx_node, row))
                        chart_txt.append(mc_connection_node_str(gc_node, gcx_node))
                    else:
                        chart_txt.append(mc_unknown_node_str(gcx_node, row))
                        chart_txt.append(mc_connection_node_str(gc_node, gcx_node))
        return chart_txt


# The null GC node is used to indicate that a GC does not exist. It is therefore not a leaf node but
# if bot GCA and GCB are NULL_GC_NODE then it is a leaf node.
NULL_GC_NODE = GCNode(ExecutionContext(), NULL_GC, None)


def node_graph(ec: ExecutionContext, gc: GCABC, limit: int) -> GCNode:
    """Build the bi-directional graph of GC's.

    The graph is a graph of GCNode objects. A GCNode object for a GC references nodes
    for each of its GCA & GCB if they exist. Note that the graph is a representation
    of the GC implementation and so each node is an instance of a GC not a definition.
    i.e. the same GC may appear multiple times in the graph. This matters because each instance
    may be implemented differently depending on what other GC's are local to it in the GC structure
    graph.

    Args:
        ec: The execution context in which the code will be defined.
        gc: Is the root of the graph.
        limit: The maximum number of lines per function

    Returns:
        GCNode: The graph root node.
    """
    assert (
        2 <= limit <= 2**15 - 1
    ), f"Invalid function maximum lines limit: {limit} must be 2 <= limit <= 32767"

    half_limit: int = limit // 2
    node_stack: list[GCNode] = [gc_node_graph := GCNode(ec, gc, None)]

    # Define the GCNode data
    while node_stack:
        # See [Assessing a GC for Function Creation](docs/executor.md) for more information.
        node: GCNode = node_stack.pop(0)
        for row, xgc in (x for x in (("A", node.gca), ("B", node.gcb)) if x[1] is not NULL_GC):
            gc_node_graph_entry: GCNode = GCNode(ec, xgc, node)
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
                    # For the purposes of this execution context the node is 1 line
                    # (the function call)
                    gc_node_graph_entry.assess = False
                    gc_node_graph_entry.exists = True
                    gc_node_graph_entry.terminal = True
                    gc_node_graph_entry.num_lines = 1
            else:
                node_stack.append(gc_node_graph_entry)
        if node.gca is NULL_GC and node.gcb is NULL_GC:
            # This is a leaf GC i.e. a codon
            node.num_lines = 1
            node.assess = False
            node.terminal = True
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
    node.write = not node.exists
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


def code_graph(function: GCNode) -> GCNode:
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

    # If the GC is a codon then there are no connections to make
    if node.gca is NULL_GC and node.gcb is NULL_GC:
        return node
    connection_stack: list[CodeConnection] = code_connection_from_iface(node, DestinationRow.O)

    # Work through the connections until they all have terminal sources and destinations
    while connection_stack:
        connection: CodeConnection = connection_stack[-1]
        src: CodeEndPoint = connection.src
        node: GCNode = src.node
        terminal_connections: list[CodeConnection] = node.terminal_connections

        # If this node is conditional a connection to row F must be made
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

    # Return the original node with the connections made
    return function


def write_gc_executable(
    ec: ExecutionContext, gc: GCABC | bytes, limit: int = 20
) -> tuple[list[str], list[str]]:
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
    gc_node_graph: GCNode = node_graph(ec, _gc, limit)
    line_count(gc_node_graph, limit)
    gcs_to_write: list[GCNode] = gc_node_graph.create_code_graphs()

    return [], []
