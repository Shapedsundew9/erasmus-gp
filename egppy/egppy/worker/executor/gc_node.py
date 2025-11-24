"""GCNode module."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Iterator
from itertools import count
from typing import TYPE_CHECKING

from egpcommon.properties import CGraphType
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph_constants import DstRow, Row, SrcRow
from egppy.genetic_code.genetic_code import (
    MERMAID_BLUE,
    MERMAID_FOOTER,
    MERMAID_GREEN,
    MERMAID_HEADER,
    MERMAID_RED,
    mc_circle_str,
    mc_connect_str,
    mc_hexagon_str,
    mc_rectangle_str,
)
from egppy.genetic_code.ggc_class_factory import GCABC, NULL_GC, NULL_SIGNATURE
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.json_cgraph import c_graph_type
from egppy.worker.executor.function_info import NULL_FUNCTION_MAP, FunctionInfo

if TYPE_CHECKING:
    from egppy.worker.executor.code_connection import CodeConnection


# Mermaid Chart creation helper function
def mc_gc_node_str(gcnode: GCNode, row: Row, color: str = "") -> str:
    """Return a Mermaid Chart string representation of the GCNode in the logical structure.
    By default a blue rectangle is used for a GC unless it is a codon which is a green circle.
    If a color is specified then that color rectangle is used.
    """
    if color == "":
        color = MERMAID_BLUE
        if gcnode.is_codon:
            if gcnode.is_meta:
                return mc_meta_node_str(gcnode, row)
            return mc_codon_node_str(gcnode, row)
    label = f'"{gcnode.gc["signature"].hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_rectangle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_unknown_node_str(gcnode: GCNode, row: Row, color: str = MERMAID_RED) -> str:
    """Return a Mermaid Chart string representation of the unknown structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc["signature"].hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_circle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_codon_node_str(gcnode: GCNode, row: Row, color: str = MERMAID_GREEN) -> str:
    """Return a Mermaid Chart string representation of the codon structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc["signature"].hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_circle_str(gcnode.uid, label, color)


# Mermaid Chart creation helper function
def mc_meta_node_str(gcnode: GCNode, row: Row, color: str = MERMAID_GREEN) -> str:
    """Return a Mermaid Chart string representation of the meta-codon structure
    GCNode in the logical structure."""
    label = f'"{gcnode.gc["signature"].hex()[-8:]}<br>{row}: {gcnode.num_lines} lines"'
    return mc_hexagon_str(gcnode.uid, label, color)


def mc_code_node_str(gcnode: GCNode) -> str:
    """Return a Mermaid Chart string representation of the code (terminal GCNode)."""
    if gcnode.exists or gcnode.write:
        # Stub ivns for the call string to keep the length under control.
        label = f"{gcnode.finfo.call_str('')}<br>{gcnode.gc['signature'].hex()[-8:]}"
        return mc_rectangle_str(gcnode.uid, label, MERMAID_GREEN)
    assert (
        gcnode.is_codon
    ), "If the GC function does not exist and is not going to, it must be a codon."
    if not gcnode.is_meta:
        label = f"{gcnode.gc['inline']}<br>{gcnode.gc['signature'].hex()[-8:]}"
        return mc_circle_str(gcnode.uid, label, MERMAID_GREEN)
    label = f"is({gcnode.gc['cgraph']['Od'][0].typ.name})<br>{gcnode.gc['signature'].hex()[-8:]}"
    return mc_hexagon_str(gcnode.uid, label, MERMAID_GREEN)


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
    namea = src.node.uid if src.node is not root and src.row is not SrcRow.I else src.node.uid + "I"
    nameb = dst.node.uid if dst.node is not root and dst.row is not DstRow.O else dst.node.uid + "O"
    return mc_connect_str(namea, nameb, arrow)


class GCNodeIterator(Iterator):
    """An iterator for the entire GCNode graph."""

    __slots__ = ("_visted", "stack")

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
            assert node != node.gca_node, "GCNode graph contains a cycle."
            self.stack.append(node)


class GCNodeCodeIterator(Iterator):
    """An iterator for only inline nodes of the graph.
    i.e. nodes that have been or will be written as functions
    are not iterated deeper than the root node.
    """

    __slots__ = ("_visted", "stack")

    def __init__(self, root) -> None:
        """Create an iterator for the GCNode graph.
        Start the iterator at the 1st codon on the execution path (the
        codon terminating the GCA->GCA->GCA...->GCA chain)
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

    __slots__ = ("root",)

    def __init__(self, root) -> None:
        self.root = root

    def __iter__(self) -> Iterator[GCNode]:
        return GCNodeCodeIterator(self.root)


class GCNode(Iterable, Hashable):
    """A node in the Connection Graph."""

    __slots__ = (
        "gc",
        "is_codon",
        "is_meta",
        "is_pgc",
        "unknown",
        "exists",
        "finfo",
        "write",
        "assess",
        "gca",
        "gcb",
        "terminal",
        "f_connection",
        "graph_type",
        "is_conditional",
        "is_loop",
        "condition_var_name",
        "gca_node",
        "gcb_node",
        "uid",
        "iam",
        "parent",
        "terminal_connections",
        "num_lines",
        "local_counter",
    )

    # For generating UIDs for GCNode instances
    _uid_counter = count()

    def __init__(
        self,
        gc: GCABC,
        parent: GCNode | None,
        row: Row,
        finfo: FunctionInfo,
        gpi: GenePoolInterface | None = None,
        wmc: bool = False,
    ) -> None:
        self.gc: GCABC = gc  # GCABC instance for this work dictionary

        # Defaults. These may be changed depending on the GC structure and what
        # is found in the cache.
        self.is_codon: bool = gc.is_codon()  # Is this node for a codon?
        self.is_meta: bool = gc.is_meta()  # Is this node for a meta-codon?
        self.unknown: bool = False  # Is this node for an unknown executable?
        self.exists: bool = finfo is not NULL_FUNCTION_MAP
        self.finfo: FunctionInfo = finfo
        self.write: bool = False  # True if the node is to be written as a function
        self.assess: bool = True  # True if the number of lines has not been determined
        self.gca: GCABC | bytes = gc["gca"]
        self.gcb: GCABC | bytes = gc["gcb"]
        self.terminal: bool = False  # A terminal node is where a connection ends
        # Cache the graph type to avoid repeated lookups
        self.graph_type: CGraphType = (
            c_graph_type(gc["cgraph"]) if gc is not NULL_GC else CGraphType.UNKNOWN
        )
        # Set conditional flags based on graph type
        self.is_conditional: bool = self.graph_type in (CGraphType.IF_THEN, CGraphType.IF_THEN_ELSE)
        self.is_loop: bool = self.graph_type in (CGraphType.FOR_LOOP, CGraphType.WHILE_LOOP)
        self.f_connection: bool = self.is_conditional
        self.condition_var_name: str | None = None
        self.is_pgc: bool = gc.is_pgc()
        # If this node is a null GC node then it is a leaf node and we self
        # reference with GCA & GCB to terminate the recursion.
        # NOTE: Not entirely comfortable with this & its potential consequences.
        self.gca_node: GCNode = NULL_GC_NODE if gc is not NULL_GC else self
        self.gcb_node: GCNode = NULL_GC_NODE if gc is not NULL_GC else self
        # Uniquely identify the node in the graph
        self.uid: str = f"uid{next(self._uid_counter):04x}"
        # List of code connections that terminate at this node if it is to be written
        self.terminal_connections: list[CodeConnection] = []
        # Calculated number of lines in the *potential* function
        self.num_lines: int = self.finfo.line_count
        # Sanity check
        assert (
            self.is_codon and not self.num_lines
        ) or not self.is_codon, "At this point a codon must have 0 lines."
        # The local variable counter (used to make unique variable names)
        self.local_counter: count[int] = count()

        # Context within the GC Node graph not known from within the GC
        if parent is None:
            # This is the top level GC that is being analysed to create a function
            # It has no parent.
            # NOTE: The top level GC is the root of the graph & therefore not terminal.
            # However, connection to its inputs and outputs are terminal.
            self.iam = SrcRow.I
            self.parent = NULL_GC_NODE if gc is not NULL_GC else self
        else:
            self.iam = row
            assert parent.gcb is gc or parent.gca is gc, "GC is neither GCA or GCB"
            self.parent = parent

        if self.is_codon:
            assert (
                self.gca is NULL_GC or self.gca == NULL_SIGNATURE
            ), "GCA must be NULL_GC for a codon"
            assert (
                self.gcb is NULL_GC or self.gcb == NULL_SIGNATURE
            ), "GCB must be NULL_GC for a codon"

            # Make sure we are not holding bytes for GCA or GCB
            self.gca = NULL_GC
            self.gcb = NULL_GC

            self.assess = False  # No need to assess a codon. We know what it is.
            self.terminal = True  # A codon is a terminal node
            # A codon is a single line of code (unless we are supressing meta-codons
            # in which case they will not be written and are thus contribute 0 lines)
            self.num_lines = int(wmc or not self.is_meta)

        if not self.exists and not self.is_codon:
            # The GC may have an unknown structure but there is no existing executable
            # Need to pull the GC sub-GC's into cache to assess it
            # The GPI is required to be initialized before we get here and a ValueError
            # will be raised if it is not.
            assert gpi is not None, "A GenePoolInterface must be provided."
            if isinstance(self.gca, bytes):
                self.gca = gpi[self.gca]
            if isinstance(self.gcb, bytes):
                self.gcb = NULL_GC if self.gcb == NULL_SIGNATURE else gpi[self.gcb]

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
            f"title: \"{self.gc['signature'].hex()[-8:]} = {self.finfo.call_str('')}\"",
            "---",
        ]
        chart_txt: list[str] = []
        if len(self.gc["inputs"]) > 0:
            chart_txt.append(f'    {self.uid}I["inputs"]')
        if len(self.gc["outputs"]) > 0:
            chart_txt.append(f'    {self.uid}O["outputs"]')

        # Iterate through the node graph in depth-first order (A then B)
        # The only way to know if writing meta-codons has been enabled is to check
        # the number of lines - this is a proxy rather than a direct test of the
        # execution contexts wmc flag.
        for node in (
            tn for tn in GCNodeCodeIterable(self) if tn.terminal and tn.num_lines and tn is not self
        ):
            chart_txt.append(mc_code_node_str(node))
        for connection in self.terminal_connections:
            chart_txt.append(mc_code_connection_node_str(connection, self))
        return "\n".join(title_txt + MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

    def function_def(self, hints: bool = False) -> str:
        """Return the function definition code line for the GC node.
        Args
        ----
            hints: If True then include type hints in the function definition.
        Returns
        -------
            A tuple containing the function definition string and a tuple of ImportDef instances
            that are required for any type hints.
        """
        # Define the function input parameters
        iface: Interface = self.gc["cgraph"]["Is"]
        inum: int = len(self.gc["inputs"])
        iparams = "i"

        if hints:
            # Add type hints for input parameters
            input_types = ", ".join(str(iface[i].typ) for i in range(inum))
            iparams += f": tuple[{input_types}]"

        # The RuntimeContext object is only required for PGCs
        rtctxt = "rtctxt: RuntimeContext, " if self.is_pgc else ""

        # Start building the function definition
        base_def = f"def {self.finfo.name()}({rtctxt}{iparams if inum else ''})"

        if hints:
            # Add type hints for output parameters
            onum = len(self.gc["outputs"])
            if onum > 1:
                oface = self.gc["cgraph"]["Od"]
                output_types = ", ".join(str(oface[i].typ) for i in range(onum))
                ret_type = f"tuple[{output_types}]"
            elif onum == 1:
                ret_type = str(self.gc["cgraph"]["Od"][0].typ)
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
            for gcx_node, row in ((gca_node, SrcRow.A), (gcb_node, SrcRow.B)):
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


# The null GC node is used to indicate that a GC does not exist. It is therefore not a leaf node
# unless both GCA and GCB are NULL_GC_NODE then it is a leaf node.
NULL_GC_NODE = GCNode(NULL_GC, None, DstRow.O, NULL_FUNCTION_MAP)
