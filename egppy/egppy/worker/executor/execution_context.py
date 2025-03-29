"""The Executor Module.

The classes and functions in this module support the execution of Genetic Codes.
See [The Genetic Code Executor](docs/executor.md) for more information.
"""

from __future__ import annotations

from itertools import count
from typing import Any

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.common import NULL_STR
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.end_point.import_def import ImportDef
from egppy.gc_graph.typing import DestinationRow, SourceRow
from egppy.gc_types.gc import (
    GCABC,
    NULL_GC,
)
from egppy.worker.gc_store import GGC_CACHE
from egppy.worker.executor.function_info import FunctionInfo, NULL_FUNCTION_MAP, NULL_EXECUTABLE
from egppy.worker.executor.gc_node import GCNode, GCNodeCodeIterable, NULL_GC_NODE
from egppy.worker.executor.fw_config import FWConfig, FWCONFIG_DEFAULT
from egppy.worker.executor.code_connection import (
    CodeConnection,
    CodeEndPoint,
    code_connection_from_iface,
)

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

    def code_graph(self, root: GCNode) -> GCNode:
        """The inputs and outputs of each function are determined by the connections between GC's.
        This function traverses the function sub-graph and makes the connections between terminal
        nodes. Since only destination endpoints are required to be connected the connections are
        made from the destination to the source (this avoids writing out "dead code").

        1. Start at the top level GC (root of the function graph).
        2. Create code_connection objects for each output of the GC.
        3. Push them individually onto the work stack.
        4. Work through the stack until all connections are terminal.
            a. If a source code end point is not terminal find what it is connected to
            and push it onto the stack.
            b. If a destination code end point is not terminal find what it is connected to
            and push it onto the stack.
        """
        node: GCNode = root  # This is the root of the graph for the GC function to be written

        # Debugging
        # _logger.debug("Creating code graph for: %s", node)

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
                        if node is not root:
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
        return root

    def code_lines(
        self, root: GCNode, lean: bool, fwconfig: FWConfig
    ) -> tuple[set[ImportDef], list[str]]:
        """Return the code lines for the GC function.
        First list are the imports and the second list are the function lines.
        """
        if not root.write:
            return set(), []

        # Comment lines at the top of the function are done first
        code: list[str] = []
        if not lean:
            if fwconfig.signature:
                code.append(f"# Signature: {root.gc['signature'].hex()}")
            if fwconfig.created:
                code.append(f"# Created: {root.gc['created']}")
            if fwconfig.license:
                code.append(f"# License: {root.gc.get('license', "MIT")}")
            if fwconfig.creator:
                code.append(f"# Creator: {root.gc['creator']}")
            if fwconfig.generation:
                code.append(f"# Generation: {root.gc['generation']}")
            if fwconfig.version and "version" in root.gc:
                code.append(f"# Version: {root.gc['version']}")
            if fwconfig.optimisations:
                code.append("# Optimisations:")
                code.append("#   - Dead code elimination: True")
                code.append(f"#   - Constant evaluation: {fwconfig.const_eval}")
                code.append(f"#   - Common subexpression elimination: {fwconfig.cse}")
                code.append(f"#   - Simplification: {fwconfig.simplification}")

        imports: set[ImportDef] = set()
        ovns: list[str] = self.name_connections(root)

        # Apply optimisations
        if lean or fwconfig.const_eval:
            self.constant_evaluation(root)
        if lean or fwconfig.cse:
            self.common_subexpression_elimination(root)
        if lean or fwconfig.simplification:
            self.simplification(root)

        # Write a line for each terminal node in the graph
        for node in (tn for tn in GCNodeCodeIterable(root) if tn.terminal and tn is not root):
            imports.update(node.gc["imports"])
            code.append(self.inline_cstr(root=root, node=node))

        # Add a return statement if the function has outputs
        if root.gc["num_outputs"] > 0:
            code.append(f"return {', '.join(ovns)}")
        return imports, code

    def common_subexpression_elimination(self, root: GCNode) -> None:
        """Apply common subexpression elimination to the GC function.
        This optimisations identifies code paths that have identical expressions
        and replaces them with a single expression that is assigned to a variable.
        """

    def constant_evaluation(self, root: GCNode) -> None:
        """Apply constant evaluation to the GC function.
        This optimisations identifies code paths that always return the same result
        and replaces them with the constant result.
        """

    def create_code_graphs(self, root: GCNode) -> list[GCNode]:
        """Return the list of GCNode instances that need to be written. i.e. that need code graphs.
        If a node (function) is not yet written it has not been assigned a global index.
        """
        nwcg: list[GCNode] = [self.code_graph(gcng) for gcng in root if gcng.write]

        for node in nwcg:
            # Set the global index for the node in execution context
            # A node will use the same index as an identical node in the same context
            # for code reuse. Naming must happen before the function is defined.
            self.new_function_placeholder(node)

        for node in nwcg:
            # Define the function in the execution context. Defining the function may involve
            # calling other functions not yet defined. This is why the function must be named
            # before it is defined.
            self.new_function(node)

        return nwcg

    def define(self, code: str) -> None:
        """Define a function in the execution context."""
        exec(code, self.namespace)  # pylint: disable=exec-used

    def function_def(
        self, node: GCNode, lean: bool = True, fwconfig: FWConfig = FWCONFIG_DEFAULT
    ) -> tuple[str, str]:
        """Create the function definition in the execution context including the imports."""
        imports, code = self.code_lines(node, lean, fwconfig)
        self.imports.update(imports)
        code.insert(0, node.function_def(fwconfig.hints and not lean))
        return "\n".join(str(imp) for imp in imports), "\n\t".join(code)

    def inline_cstr(self, root: GCNode, node: GCNode) -> str:
        """Return the code string for the GC inline code."""
        # By default the ovns is underscore (unused) for all outputs. This is
        # then overridden by any connection that starts (is source endpoint) at this node.
        ovns: list[str] = ["_"] * node.gc["num_outputs"]
        rtc: list[CodeConnection] = root.terminal_connections
        for ovn, idx in ((c.var_name, c.src.idx) for c in rtc if c.src.node is node):
            ovns[idx] = ovn

        # Similary the ivns are defined. However, they must have variable names as they
        # cannot be undefined.
        ivns: list[str] = [NULL_STR] * node.gc["num_inputs"]
        for ivn, idx in ((c.var_name, c.dst.idx) for c in rtc if c.dst.node is node):
            ivns[idx] = ivn

        # Is this node a codon?
        assignment = ", ".join(ovns) + " = "
        if node.is_codon:
            ivns_map: dict[str, str] = {f"i{i}": ivn for i, ivn in enumerate(ivns)}
            return assignment + node.gc["inline"].format_map(ivns_map)
        return assignment + node.function_info.call_str(ivns)

    def line_limit(self) -> int:
        """Return the maximum number of lines in a function."""
        return self._line_limit

    def name_connections(self, root: GCNode) -> list[str]:
        """Name the source variable of the connection between two code end points."""

        # Gather the output variable names to catch the case where an input is
        # directly connected to an output
        _ovns: list[str] = ["" for _ in range(root.gc["num_outputs"])]
        root.terminal_connections.sort(key=connection_key)
        for connection in root.terminal_connections:
            # If the source end point has already had a variable name assigned
            # then the connection is already named.
            dst: CodeEndPoint = connection.dst
            if connection.var_name is NULL_STR:

                # Quick reference the source code endpoint,
                # the output variable names and the output index
                src: CodeEndPoint = connection.src
                idx: int = src.idx

                # Priority naming is given to input and output variables
                # This keeps all inputs as ix and outputs as ox except in the
                # case where the input is directly connected to the output.
                if src.row == SourceRow.I:
                    assert src.node is root, "Invalid connection source node."
                    assert connection.var_name == "", "Input variable name already assigned."
                    connection.var_name = i_cstr(idx)
                elif dst.row == DestinationRow.O and connection.var_name is NULL_STR:
                    assert dst.node is root, "Invalid connection destination node."
                    connection.var_name = o_cstr(dst.idx)
                elif connection.var_name is NULL_STR:
                    assert src.row == SourceRow.A or src.row == SourceRow.B, "Invalid source row."
                    number = next(root.local_counter)
                    connection.var_name = t_cstr(number)
                else:
                    raise ValueError("Invalid connection source row.")

            # Gather the outputs for this node (may not be named ox if connected to an input)
            if dst.row == DestinationRow.O:
                assert dst.node is root, "Invalid connection destination node."
                _ovns[dst.idx] = connection.var_name
        return _ovns

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
            _logger.debug("Function:\n%s", node.function_info.name())
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
        finfo = self.function_map.get(gc["signature"], NULL_FUNCTION_MAP)
        node_stack: list[GCNode] = [gc_node_graph := GCNode(gc, None, SourceRow.I, finfo)]

        # Define the GCNode data
        while node_stack:
            # See [Assessing a GC for Function Creation](docs/executor.md) for more information.
            node: GCNode = node_stack.pop(0)
            # if _LOG_DEBUG:
            # _logger.debug("Assessing node: %s", node)
            if node.is_codon or node.unknown:
                continue
            child_nodes = ((DestinationRow.A, node.gca), (DestinationRow.B, node.gcb))
            for row, xgc in (x for x in child_nodes):
                assert isinstance(xgc, GCABC), "GCA or GCB must be a GCABC instance"
                fmap = self.function_map.get(xgc["signature"], NULL_FUNCTION_MAP)
                gc_node_graph_entry: GCNode = GCNode(xgc, node, row, fmap)
                if row == DestinationRow.A:
                    node.gca_node = gc_node_graph_entry
                else:
                    node.gcb_node = gc_node_graph_entry
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
                        gc_node_graph_entry.num_lines = 1
                else:
                    node_stack.append(gc_node_graph_entry)
        return gc_node_graph

    def simplification(self, root: GCNode) -> None:
        """Apply simplification to the GC function.
        This optimisations uses symbolic regression to simplify the code.
        """

    def write_executable(self, gc: GCABC | bytes) -> GCNode | None:
        """Write the code for the GC.

        Sub-GC's are looked up in the gc_store.
        The returned lists are the imports and functions.
        Note that functions will be between limit/2 and limit lines long.

        1. Graph bi-directional graph of GC's

        Args:
            gc_store (CacheABC): The cache of GC's.
            gc (GCABC | bytes): The Genetic Code.
            limit (int, optional): The maximum number of lines per function. Defaults to 20.

        Returns:
            GCNode: The GC node graph or None if the GC already exists as a suitable function.
        """
        sig: bytes = gc.signature() if isinstance(gc, GCABC) else gc
        assert isinstance(sig, bytes), f"Invalid signature type: {type(sig)}"

        # Function already exists & is a reasonable size
        if sig in self.function_map and self.function_map[sig].line_count > self._line_limit // 2:
            return None

        # The GC may have been assessed as part of another GC but not an executable in its own right
        # The GC node graph is needed to determine connectivity and so we reset the num_lines
        # and re-assess
        _gc: GCABC = gc if isinstance(gc, GCABC) else GGC_CACHE[sig]
        gc_node_graph: GCNode = self.node_graph(_gc)
        gc_node_graph.line_count(self._line_limit)
        self.create_code_graphs(gc_node_graph)
        return gc_node_graph
