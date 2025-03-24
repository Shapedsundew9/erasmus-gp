"""The Executor Module.

The classes and functions in this module support the execution of Genetic Codes.
See [The Genetic Code Executor](docs/executor.md) for more information.
"""

from __future__ import annotations

from collections.abc import Hashable, Sequence, Iterable, Iterator
from dataclasses import dataclass
from itertools import count
from typing import Any, Callable

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.common import NULL_STR

from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.end_point.end_point_type import ept_to_str
from egppy.gc_graph.end_point.import_def import ImportDef
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
from egppy.worker.gc_store import GGC_CACHE

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
enable_debug_logging()
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Constants
# Maximum number of local variables in a GC function
# Limit is representation as a variable name f"t{number:05d}"
MAX_NUM_LOCALS: int = 99999
UNUSED_VAR_NAME: str = "_"


# For GC's with no executable (yet)
def NULL_EXECUTABLE(_: tuple) -> tuple:  # pylint: disable=invalid-name
    """The Null Exectuable. Should never be executed."""
    raise RuntimeError("NULL_EXECUTABLE should never be executed.")


# For sorting connections for naming
def connection_key(connection: CodeConnection) -> int:
    """Return the key for sorting connections for naming.
    Input connections where the source is the top level node are first.
    Output connections where the destination is the top level node are second.
    All other connections are last.

    This ensures inputs get assigned an ix name and outputs a ox name.
    Everything else is assigned a tx name.
    """
    if connection.src.row == SourceRow.I:
        return 0
    if connection.dst.row == DestinationRow.O:
        return 1
    return 2


def i_cstr(n: int) -> str:
    """Return the code string for the nth input.
    GC inputs are always implemented as a tuple named 'i'.
    The number of inputs is limited to 256 in a GC.
    """
    assert 0 <= n <= 255, f"Invalid input index: {n} must be 0 <= n <= 255"
    return f"i[{n}]"


def o_cstr(n: int) -> str:
    """Return the code string for the nth output variable.
    Output variables are assigned to.
    The number of outputs in a GC is limited to 256.
    """
    assert 0 <= n <= 255, f"Invalid output index: {n} must be 0 <= n <= 255"
    return f"o{n}"


def t_cstr(n: int) -> str:
    """Return the code string for the nth temporary variable.
    Temporary variables are assigned to.
    The number of temporary variables in a function is limited to 100,000.
    """
    assert 0 <= n <= 99999, f"Invalid temporary index: {n} must be 0 <= n <= 99999"
    return f"t{n}"


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


@dataclass
class FunctionInfo:
    """The information for a function in the execution context."""

    executable: Callable
    global_index: int
    line_count: int
    gc: GCABC

    def name(self) -> str:
        """Return the function name."""
        return f"f_{self.global_index:x}"

    def call_str(self, ivns: Sequence[str]) -> str:
        """Return the function call string using the map of input variable names."""
        if len(ivns):
            return f"{self.name()}(({', '.join(f'{ivn}' for ivn in ivns)},))"
        return f"{self.name()}()"


NULL_FUNCTION_MAP: FunctionInfo = FunctionInfo(NULL_EXECUTABLE, -1, 0, NULL_GC)


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

    def __init__(self, line_limit: int = 64) -> None:
        # The globals passed to exec() when defining objects in the context
        self.namespace: dict[str, Any] = {}
        # Used to uniquely name objects in this context
        self._global_index = count()
        # Map signatures to functions, global index & line count
        self.function_map: dict[bytes, FunctionInfo] = {}
        # The maximum number of lines in a function
        self._line_limit: int = line_limit
        # Existing Imports
        self.imports: set[ImportDef] = set()

    def define(self, code: str) -> None:
        """Define a function in the execution context."""
        exec(code, self.namespace)  # pylint: disable=exec-used

    def function_def(self, node: GCNode) -> tuple[str, str]:
        """Create the function definition in the execution context including the imports."""
        imports, code = node.code_lines()
        self.imports.update(imports)
        code.insert(0, node.function_def())
        return "\n".join(str(imp) for imp in imports), "\n\t".join(code)

    def line_limit(self) -> int:
        """Return the maximum number of lines in a function."""
        return self._line_limit

    def new_function_placeholder(self, node: GCNode) -> FunctionInfo:
        """Create a placeholder for a new function in the execution context.
        Functions need to be named before they can be defined otherwise they would
        have to be defined in the order they are used which is not always possible.
        """
        signature = node.gc["signature"]
        self.function_map[signature] = newf = FunctionInfo(
            NULL_EXECUTABLE, next(self._global_index), node.num_lines, node.gc
        )
        node.function_info = newf
        return newf

    def new_function(self, node: GCNode) -> FunctionInfo:
        """Create a new function in the execution context."""
        imports, code = self.function_def(node)

        # Debugging
        if _LOG_DEBUG:
            _logger.debug("Function: %s", node.function_info.name())
            _logger.debug("Imports:\n%s", imports)
            _logger.debug("Code:\n%s", code)

        # Add to the execution context
        self.define(imports)
        self.define(code)
        node.function_info.executable = self.namespace[node.function_info.name()]
        return node.function_info

    def node_graph(self, gc: GCABC) -> GCNode:
        """Build the bi-directional graph of GC's.

        The graph is a graph of GCNode objects. A GCNode object for a GC references nodes
        for each of its GCA & GCB if they exist. Note that the graph is a representation
        of the GC implementation and so each node is an instance of a GC not a definition.
        i.e. the same GC may appear multiple times in the graph. This matters because each
        instance may be implemented differently depending on what other GC's are local to
        it in the GC structure graph.

        Args:
            gc: Is the root of the graph.

        Returns:
            GCNode: The graph root node.
        """
        assert (
            2 <= self._line_limit <= 2**15 - 1
        ), f"Invalid lines limit: {self._line_limit} must be 2 <= limit <= 32767"

        half_limit: int = self._line_limit // 2
        node_stack: list[GCNode] = [gc_node_graph := GCNode(self, gc, None, SourceRow.I)]

        # Define the GCNode data
        while node_stack:
            # See [Assessing a GC for Function Creation](docs/executor.md) for more information.
            node: GCNode = node_stack.pop(0)
            # if _LOG_DEBUG:
            _logger.debug("Assessing node: %s", node)
            if node.is_codon or node.unknown:
                continue
            child_nodes = ((DestinationRow.A, node.gca), (DestinationRow.B, node.gcb))
            for row, xgc in (x for x in child_nodes):
                assert isinstance(xgc, GCABC), "GCA or GCB must be a GCABC instance"
                gc_node_graph_entry: GCNode = GCNode(self, xgc, node, row)
                if row == DestinationRow.A:
                    node.gca_node = gc_node_graph_entry
                else:
                    node.gcb_node = gc_node_graph_entry
                fmap: FunctionInfo = self.function_map.get(xgc["signature"], NULL_FUNCTION_MAP)
                assert (
                    fmap.line_count <= self._line_limit
                ), f"# lines in function exceeds limit: {fmap.line_count} > {self._line_limit}"
                if fmap.executable is not NULL_EXECUTABLE:  # A known executable
                    assert (
                        fmap.line_count > 0
                    ), f"The # lines cannot be <= 0 when there is an executable: {fmap.line_count}"
                    if fmap.line_count < half_limit:
                        node_stack.append(gc_node_graph_entry)
                    else:
                        # Existing executable is suitable (so no need to assess or write it)
                        # For the purposes of this execution context the node is 1 line
                        # (the function call)
                        gc_node_graph_entry.assess = False
                        gc_node_graph_entry.exists = True
                        gc_node_graph_entry.terminal = True
                        gc_node_graph_entry.function_info.line_count = 1
                else:
                    node_stack.append(gc_node_graph_entry)
        return gc_node_graph

    def write_executable(self, gc: GCABC | bytes) -> None:
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

        # Function already exists & is a reasonable size
        if sig in self.function_map and self.function_map[sig].line_count > self._line_limit // 2:
            return

        # The GC may have been assessed as part of another GC but not an executable in its own right
        # The GC node graph is needed to determine connectivity and so we reset the num_lines
        # and re-assess
        _gc: GCABC = gc if isinstance(gc, GCABC) else GGC_CACHE[sig]
        gc_node_graph: GCNode = self.node_graph(_gc)
        gc_node_graph.line_count()
        gc_node_graph.create_code_graphs()


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
        # If a is to be written then there is no need to go any further
        # as the parent will become a single line executable in this code. The exception
        # is if the parent is the root which by definition is being written and this code is
        # figuring out how.
        # NB: If a parent exists it does not mean it will be used (it may have too few lines)
        while (parent is root or not parent.write) and (node is not NULL_GC_NODE):
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

    def __init__(self, ec: ExecutionContext, gc: GCABC, parent: GCNode | None, row: Row) -> None:
        self.ec: ExecutionContext = ec  # The execution context for this work dictionary
        self.gc: GCABC = gc  # GCABC instance for this work dictionary

        # Defaults. These may be changed depending on the GC structure and what
        # is found in the cache.
        self.is_codon: bool = False  # Is this node for a codon?
        self.unknown: bool = False  # Is this node for an unknown executable?
        self.exists: bool = gc["signature"] in self.ec.function_map
        self.function_info = self.ec.function_map.get(gc["signature"], NULL_FUNCTION_MAP)
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
        self._local_counter = count()

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

    def create_code_graphs(self) -> list[GCNode]:
        """Return the list of GCNode instances that need to be written. i.e. that need code graphs.
        If a node (function) is not yet written it has not been assigned a global index.
        """
        nwcg: list[GCNode] = [code_graph(gcng) for gcng in self if gcng.write]

        for node in nwcg:
            # Set the global index for the node in execution context
            # A node will use the same index as an identical node in the same context
            # for code reuse. Naming must happen before the function is defined.
            self.ec.new_function_placeholder(node)

        for node in nwcg:
            # Define the function in the execution context. Defining the function may involve
            # calling other functions not yet defined. This is why the function must be named
            # before it is defined.
            self.ec.new_function(node)

        return nwcg

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

    def inline_cstr(self, root: GCNode) -> str:
        """Return the code string for the GC inline code."""
        # By default the ovns is underscore (unused) for all outputs. This is
        # then overridden by any connection that starts (is source endpoint) at this node.
        ovns: list[str] = ["_"] * self.gc["num_outputs"]
        rtc = root.terminal_connections
        for ovn, idx in ((c.var_name, c.src.idx) for c in rtc if c.src.node is self):
            ovns[idx] = ovn

        # Similary the ivns are defined. However, they must have variable names as they
        # cannot be undefined.
        ivns: list[str] = [NULL_STR] * self.gc["num_inputs"]
        for ivn, idx in ((c.var_name, c.dst.idx) for c in rtc if c.dst.node is self):
            ivns[idx] = ivn

        # Is this node a codon?
        assignment = ", ".join(ovns) + " = "
        if self.is_codon:
            ivns_map: dict[str, str] = {f"i{i}": ivn for i, ivn in enumerate(ivns)}
            return assignment + self.gc["inline"].format_map(ivns_map)
        return assignment + self.function_info.call_str(ivns)

    def line_count(self) -> None:
        """Calculate the best number of lines for each function and
        mark the ones that should be written. This function traverses the graph
        starting at the root and working down to the leaves (codons) and then
        back up to the root accumulating line counts.

        When a node that meets the criteria to be written is found then the node is marked
        as to be written, terminal and the line count is set. The node is then marked as
        no longer needing assessment.
        """
        node: GCNode = self
        limit = node.ec.line_limit()
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

    def name_connections(self) -> list[str]:
        """Name the source variable of the connection between two code end points."""

        # Gather the output variable names to catch the case where an input is
        # directly connected to an output
        _ovns: list[str] = ["" for _ in range(self.gc["num_outputs"])]
        self.terminal_connections.sort(key=connection_key)
        src_cep_map: dict[CodeEndPoint, CodeConnection] = {}
        for connection in self.terminal_connections:
            # If the source end point has already had a varibale name assigned
            # then the connection is already named.
            src: CodeEndPoint = connection.src
            if src in src_cep_map:
                connection.var_name = src_cep_map[src].var_name
                continue
            src_cep_map[src] = connection

            # Quick reference the source code endpoint,
            # the output variable names and the output index
            dst: CodeEndPoint = connection.dst
            idx: int = src.idx

            # Priority naming is given to input and output variables
            # This keeps all inputs as ix and outputs as ox except in the
            # case where the input is directly connected to the output.
            if src.row == SourceRow.I:
                assert src.node is self, "Invalid connection source node."
                assert connection.var_name == "", "Input variable name already assigned."
                connection.var_name = i_cstr(idx)
            elif dst.row == DestinationRow.O and connection.var_name is NULL_STR:
                assert dst.node is self, "Invalid connection destination node."
                connection.var_name = o_cstr(dst.idx)
            elif connection.var_name is NULL_STR:
                assert src.row == SourceRow.A or src.row == SourceRow.B, "Invalid source row."
                number = next(self._local_counter)
                connection.var_name = t_cstr(number)
            else:
                raise ValueError("Invalid connection source row.")

            # Gather the outputs for this node (may not be named ox if connected to an input)
            if dst.row == DestinationRow.O:
                assert dst.node is self, "Invalid connection destination node."
                _ovns[dst.idx] = connection.var_name
        return _ovns

    def code_lines(self) -> tuple[set[ImportDef], list[str]]:
        """Return the code lines for the GC function.
        First list are the imports and the second list are the function lines.
        """
        if not self.write:
            return set(), []
        imports: set[ImportDef] = set()
        code: list[str] = []
        ovns: list[str] = self.name_connections()

        # Write a line for each terminal node in the graph
        for node in (tn for tn in GCNodeCodeIterable(self) if tn.terminal and tn is not self):
            imports.update(node.gc["imports"])
            code.append(node.inline_cstr(self))

        # Add a return statement if the function has outputs
        if self.gc["num_outputs"] > 0:
            code.append(f"return {', '.join(ovns)}")
        return imports, code


# The null GC node is used to indicate that a GC does not exist. It is therefore not a leaf node but
# if bot GCA and GCB are NULL_GC_NODE then it is a leaf node.
NULL_GC_NODE = GCNode(ExecutionContext(), NULL_GC, None, DestinationRow.O)


class CodeEndPoint(Hashable):
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
        case DestinationRow.A:
            dst_node = node.gca_node
            dst_row = SourceRow.I
        case DestinationRow.B:
            dst_node = node.gcb_node
            dst_row = SourceRow.I
        case _:
            dst_node = node
            dst_row = DestinationRow.O
    return [
        CodeConnection(
            CodeEndPoint(node, r[0].get_row(), r[0].get_idx()),
            CodeEndPoint(dst_node, dst_row, i, True),
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

    # Debugging
    _logger.debug("Creating code graph for: %s", node)

    # If the GC is a codon then there are no connections to make
    if node.gca is NULL_GC and node.gcb is NULL_GC:
        return node
    connection_stack: list[CodeConnection] = code_connection_from_iface(node, DestinationRow.O)
    terminal_connections: list[CodeConnection] = node.terminal_connections

    # Make sure we are not processing the same interface more than once.
    visited_nodes: set[GCNode] = {node}

    # Work through the connections until they all have terminal sources and destinations
    while connection_stack:
        connection: CodeConnection = connection_stack[-1]
        src: CodeEndPoint = connection.src
        node: GCNode = src.node

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
                    # Function is the root node. Going to its parent is moving
                    # out of the scope of this function.
                    if node is not function:
                        # When moving into the parent the src context needs
                        # to change to that of src within the parent.
                        refs = parent.gc["graph"][node.iam + "dc"]
                        ref: XEndPointRefABC = refs[src.idx][0]
                        src.row = ref.get_row()
                        if src.row == SourceRow.I:
                            src.node = parent
                            node = parent.parent
                            # If the source in the parent it row I & its parent is the root
                            # then the source is terminal - it is a connection to the top level
                            # GC input interface.
                            src.terminal = src.node.terminal or node is NULL_GC_NODE
                        else:
                            src.node = parent.gca_node
                            refs = src.node.gc["graph"]["Odc"]
                            src.idx = ref.get_idx()
                            node = parent
                            src.terminal = src.node.terminal
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
                # If the source is terminal then add its destination interface within the node
                # to the connection stack if it has not already been added (visited).
                # node.iam tells us which row defines the interface within the node.
                assert connection.dst.terminal, "Destination must be terminal."

                # The list of connections for the entire written GC (all the local
                # variables that are defined or used in the function) are maintained
                # in the function nodes terminal_connections list.
                terminal_connections.append(connection)
                connection_stack.pop()
                if src.node not in visited_nodes:
                    visited_nodes.add(src.node)
                    connection_stack.extend(code_connection_from_iface(node, src.node.iam))
        else:
            assert False, "Source must not be terminal."

        # If this node is conditional a connection to row F must be made
        if node is not NULL_GC_NODE and node.f_connection:
            node.f_connection = False
            connection_stack.append(
                CodeConnection(
                    CodeEndPoint(node, SourceRow.I, node.gc["graph"]["Fdc"][0].get_idx()),
                    CodeEndPoint(node, DestinationRow.F, 0, True),
                )
            )

    # Return the original node with the connections made
    return function
