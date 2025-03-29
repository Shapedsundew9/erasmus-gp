"""GCNode module."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Hashable
from itertools import count
from typing import TYPE_CHECKING

from egppy.gc_graph.end_point.end_point_type import ept_to_str
from egppy.gc_graph.typing import DestinationRow, Row, SourceRow
from egppy.gc_types.gc import (
    GCABC,
    MERMAID_CODON_COLOR,
    MERMAID_FOOTER,
    MERMAID_GC_COLOR,
    MERMAID_HEADER,
    MERMAID_UNKNOWN_COLOR,
    NULL_GC,
    NULL_SIGNATURE,
    mc_circle_str,
    mc_connect_str,
    mc_rectangle_str,
)
from egppy.worker.executor.function_info import NULL_FUNCTION_MAP, FunctionInfo
from egppy.worker.gc_store import GGC_CACHE

if TYPE_CHECKING:
    from egppy.worker.executor.code_connection import CodeConnection


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
        # Stub ivns for the call string to keep the length under control.
        label = f"{gcnode.function_info.call_str('')}<br>{gcnode.gc['signature'].hex()[-8:]}"
        return mc_rectangle_str(gcnode.uid, label, "green")
    assert (
        gcnode.gc.is_codon()
    ), "If the GC function does not exist and is not going to, it must be a codon."
    label = f"{gcnode.gc['inline']}<br>{gcnode.gc['signature'].hex()[-8:]}"
    return mc_circle_str(gcnode.uid, label, "green")


# Mermaid Chart creation helper function
def mc_connection_node_str(gcnodea: GCNode, gcnodeb: GCNode) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    return mc_connect_str(gcnodea.uid, gcnodeb.uid)


# Mermaid Chart creation helper function
def mc_code_connection_node_str(connection: CodeConnection, root: GCNode) -> str:
    """Return a Mermaid Chart string representation of the connection between two nodes."""
    src = connection.src
    dst = connection.dst
    arrow = f"-- {src.idx}:{dst.idx} -->"
    namea = (
        src.node.uid if src.node is not root and src.row is not SourceRow.I else src.node.uid + "I"
    )
    nameb = (
        dst.node.uid
        if dst.node is not root and dst.row is not DestinationRow.O
        else dst.node.uid + "O"
    )
    return mc_connect_str(namea, nameb, arrow)


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

        # If the node is a terminal node then return it unless
        # it is the root node in which case we continue to explore
        # the graph to the next terminal node.
        if node.terminal and node is not self.stack[0]:
            return self.stack.pop()

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
        root = self.stack[0]
        # If a node is to be written or already terminal then there is no need to go any further
        # as the parent will become a single line executable in this code. The exception
        # is if the parent is the root which by definition is being written and this code is
        # figuring out how.
        # NB: If a parent exists it does not mean it will be used (it may have too few lines)
        while (parent is root or not (parent.write or parent.terminal)) and (
            node is not NULL_GC_NODE
        ):
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
    _uid_counter = count()

    def __init__(self, gc: GCABC, parent: GCNode | None, row: Row, finfo: FunctionInfo) -> None:
        self.gc: GCABC = gc  # GCABC instance for this work dictionary

        # Defaults. These may be changed depending on the GC structure and what
        # is found in the cache.
        self.is_codon: bool = False  # Is this node for a codon?
        self.unknown: bool = False  # Is this node for an unknown executable?
        self.exists: bool = finfo is not NULL_FUNCTION_MAP
        self.function_info: FunctionInfo = finfo
        self.write: bool = False  # True if the node is to be written as a function
        self.assess: bool = True  # True if the number of lines has not been determined
        self.gca: GCABC | bytes = gc["gca"]
        self.gcb: GCABC | bytes = gc["gcb"]
        self.terminal: bool = False  # A terminal node is where a connection ends
        self.f_connection: bool = gc.is_conditional()
        self.gca_node: GCNode = NULL_GC_NODE if gc is not NULL_GC else self
        self.gcb_node: GCNode = NULL_GC_NODE if gc is not NULL_GC else self
        # Uniquely identify the node in the graph
        self.uid: str = f"uid{next(self._uid_counter):04x}"
        # The code connection end points if this node is to be written
        self.terminal_connections: list[CodeConnection] = []
        # Calculated number of lines in the *potential* function
        self.num_lines = self.function_info.line_count
        # The local variable counter (used to make unique variable names)
        self.local_counter = count()

        # Context within the GC Node graph not known from within the GC
        if parent is None:
            # This is the top level GC that is being analysed to create a function
            # It has no parent.
            # NOTE: The top level GC is the root of the graph & therefore not terminal.
            # However, connection to its inputs and outputs are terminal.
            self.iam = SourceRow.I
            self.parent = NULL_GC_NODE if gc is not NULL_GC else self
        else:
            self.iam = row
            assert parent.gcb is gc or parent.gca is gc, "GC is neither GCA or GCB"
            self.parent = parent

        if gc.is_codon():
            self.is_codon = True  # Set is_codon to True if gc indicates a codon
            assert (
                self.gca is NULL_GC or self.gca is NULL_SIGNATURE
            ), "GCA must be NULL_GC for a codon"
            assert (
                self.gcb is NULL_GC or self.gcb is NULL_SIGNATURE
            ), "GCB must be NULL_GC for a codon"
            self.assess = False  # No need to assess a codon. We know what it is.
            self.terminal = True  # A codon is a terminal node
            self.num_lines = 1  # A codon is a single line of code

        if not self.exists and not self.is_codon:
            # The GC may have an unknown structure but there is no existing executable
            # Need to pull the GC sub-GC's into cache to assess it
            if isinstance(self.gca, bytes):
                self.gca = GGC_CACHE[self.gca]
            if isinstance(self.gcb, bytes):
                self.gcb = GGC_CACHE[self.gcb]

        if self.exists and (isinstance(self.gca, bytes) or isinstance(self.gcb, bytes)):
            # This is a unknown executable (treated like a codon in many respects)
            assert not self.is_codon, "A codon cannot be an unknown executable"
            self.terminal = True
            self.assess = False
            self.unknown = True
            self.num_lines = 1

    def __eq__(self, value: object) -> bool:
        """Return True if the GCNode instance is equal to the value."""
        if not isinstance(value, GCNode):
            return False
        return self.uid == value.uid

    def __hash__(self) -> int:
        """Return the hash of the GCNode instance."""
        return hash(self.uid)

    def __iter__(self) -> Iterator[GCNode]:
        """Return an iterator for the entire GCNode graph."""
        return GCNodeIterator(self)

    def __repr__(self) -> str:
        """Return the representation of the GCNode instance."""
        return f"GCNode({self.uid}(0x{self.gc['signature'].hex()[-8:]}), {self.iam})"

    def __str__(self) -> str:
        """Return the representation of the GCNode instance."""
        str_list: list[str] = [f"GCNode: {self.gc['signature'].hex()}"]
        for k, v in vars(self).items():
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
            f"title: \"{self.gc['signature'].hex()[-8:]} = {self.function_info.call_str('')}\"",
            "---",
        ]
        chart_txt: list[str] = []
        if self.gc["num_inputs"] > 0:
            chart_txt.append(f'    {self.uid}I["inputs"]')
        if self.gc["num_outputs"] > 0:
            chart_txt.append(f'    {self.uid}O["outputs"]')

        # Iterate through the node graph in depth-first order (A then B)
        for node in (tn for tn in GCNodeCodeIterable(self) if tn.terminal and tn is not self):
            chart_txt.append(mc_code_node_str(node))
        for connection in self.terminal_connections:
            chart_txt.append(mc_code_connection_node_str(connection, self))
        return "\n".join(title_txt + MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

    def function_def(self, hints: bool = False) -> str:
        """Return the function definition code line for the GC node.
        hints: If True then include type hints in the function definition.
        """
        # Define the function input parameters
        iface = self.gc["graph"]["Is"]
        inum = self.gc["num_inputs"]
        iparams = "i"

        if hints:
            # Add type hints for input parameters
            input_types = ", ".join(ept_to_str(iface[i]) for i in range(inum))
            iparams += f": tuple[{input_types}]"

        # Start building the function definition
        base_def = f"def {self.function_info.name()}({iparams if inum else ''})"

        if hints:
            # Add type hints for output parameters
            onum = self.gc["num_outputs"]
            if onum > 1:
                oface = self.gc["graph"]["Od"]
                output_types = ", ".join(ept_to_str(oface[i]) for i in range(onum))
                ret_type = f"tuple[{output_types}]"
            elif onum == 1:
                ret_type = ept_to_str(self.gc["graph"]["Od"][0])
            elif onum == 0:
                ret_type = "None"
            else:
                raise ValueError(f"Invalid number of outputs: {onum}, in GC.")
            return f"{base_def} -> {ret_type}:"

        # Return the function definition without type hints
        return f"{base_def}:"

    def line_count(self, limit: int) -> None:
        """Calculate the best number of lines for each function and
        mark the ones that should be written. This function traverses the graph
        starting at the root and working down to the leaves (codons) and then
        back up to the root accumulating line counts.

        When a node that meets the criteria to be written is found then the node is marked
        as to be written, terminal and the line count is set. The node is then marked as
        no longer needing assessment.
        """
        node: GCNode = self
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
NULL_GC_NODE = GCNode(NULL_GC, None, DestinationRow.O, NULL_FUNCTION_MAP)
