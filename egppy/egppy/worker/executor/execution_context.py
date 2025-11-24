"""The Executor Module.

The classes and functions in this module support the execution of Genetic Codes.
See [The Genetic Code Executor](docs/executor.md) for more information.
"""

from __future__ import annotations

from itertools import chain, count
from typing import Any

from egpcommon.common import NULL_STR
from egpcommon.egp_log import DEBUG, Logger, egp_logger, enable_debug_logging
from egpcommon.properties import CGraphType
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.ggc_class_factory import GCABC, NULL_GC
from egppy.genetic_code.import_def import ImportDef
from egppy.genetic_code.interface import Interface, unpack_src_ref
from egppy.physics.pgc_api import RuntimeContext
from egppy.worker.executor.code_connection import (
    CodeConnection,
    CodeEndPoint,
    code_connection_from_iface,
)
from egppy.worker.executor.function_info import NULL_EXECUTABLE, NULL_FUNCTION_MAP, FunctionInfo
from egppy.worker.executor.fw_config import FWCONFIG_DEFAULT, FWConfig
from egppy.worker.executor.gc_node import NULL_GC_NODE, GCNode, GCNodeCodeIterable

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
enable_debug_logging()


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
    if connection.src.row == SrcRow.I:
        return 0
    if connection.dst.row == DstRow.O:
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

    __slots__ = (
        "namespace",
        "function_map",
        "imports",
        "_line_limit",
        "_global_index",
        "wmc",
        "_codon_register",
        "gpi",
    )

    def __init__(self, gpi: GenePoolInterface, line_limit: int = 64, wmc: bool = False) -> None:
        """Create a new execution context.
        Args:
            gpi (GenePoolInterface): The gene pool interface used to look up GC's.
            line_limit (int): The maximum number of lines in a function.
            wmc (bool): Write meta-codons when True."""
        # The globals passed to exec() when defining objects in the context
        # The GenePoolInterface instance is stored in the namespace as "GPI"
        # is explicitly used in the selector codons.
        self.gpi: GenePoolInterface = gpi
        self.namespace: dict[str, Any] = {"GPI": gpi}
        # Used to uniquely name objects in this context
        self._global_index = count()
        # Map signatures to functions, global index & line count
        self.function_map: dict[bytes, FunctionInfo] = {}
        # The maximum number of lines in a function
        self._line_limit: int = line_limit
        # Existing Imports
        self.imports: set[ImportDef] = set()
        # Write Meta-Codons (these are usually used for debugging).
        self.wmc: bool = wmc
        # Codon register - codons that have been processed in this context
        # Used to save trying to re-process the same codon e.g. imports.
        self._codon_register: set[bytes] = set()

    def code_graph(self, root: GCNode) -> GCNode:
        """The inputs and outputs of each function are determined by the connections between GC's.
        This function traverses the function sub-graph and makes the connections between terminal
        nodes. Since only destination endpoints are required to be connected the connections are
        made from the destination to the source (this avoids writing out "dead code").

        1. Start at the top level GC (root of the function graph).
        2. Create code_connection objects for each output of the GC.
        3. Push them individually onto the work stack.
        4. Work through the stack until all connections are terminal.
            a. If a source code endpoint is not terminal find what it is connected to
            and push it onto the stack.
            b. If a destination code endpoint is not terminal find what it is connected to
            and push it onto the stack.
        """
        node: GCNode = root  # This is the root of the graph for the GC function to be written

        # Debugging
        # _logger.debug("Creating code graph for: %s", node)

        # Create initial connections for Row O (always present)
        connection_stack: list[CodeConnection] = code_connection_from_iface(node, DstRow.O)

        # For conditional graphs, also create connections for Row P (alternate path)
        if node.is_conditional:
            connection_stack.extend(code_connection_from_iface(node, DstRow.P))

        # For loop graphs, also create connections for L, S, W, T, X
        if node.is_loop:
            if node.graph_type == CGraphType.FOR_LOOP:
                connection_stack.extend(code_connection_from_iface(node, DstRow.L))
                connection_stack.extend(code_connection_from_iface(node, DstRow.S))
                connection_stack.extend(code_connection_from_iface(node, DstRow.T))
            elif node.graph_type == CGraphType.WHILE_LOOP:
                connection_stack.extend(code_connection_from_iface(node, DstRow.W))
                connection_stack.extend(code_connection_from_iface(node, DstRow.S))
                connection_stack.extend(code_connection_from_iface(node, DstRow.T))
                connection_stack.extend(code_connection_from_iface(node, DstRow.X))

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
                    case SrcRow.A:
                        # Special case: If this node is a codon, row A just defines the interface
                        # to the inline code, not a sub-GC. Treat it as terminal.
                        if node.is_codon:
                            src.terminal = True
                            iface: Interface | None = None
                        else:
                            assert node.gca is not NULL_GC, "Should never introspect a codon graph."
                            src.node = node.gca_node
                            src.terminal = node.gca_node.terminal
                            iface = src.node.gc["cgraph"]["Od"]
                    case SrcRow.B:
                        assert node.gcb is not NULL_GC, "GCB cannot be NULL"
                        src.node = node.gcb_node
                        src.terminal = node.gcb_node.terminal
                        iface = src.node.gc["cgraph"]["Od"]
                    case SrcRow.I | SrcRow.S | SrcRow.L | SrcRow.W:
                        parent: GCNode = node.parent
                        # Function is the root node. Going to its parent is moving
                        # out of the scope of this function.
                        if node is not root:
                            # When moving into the parent the src context needs
                            # to change to that of src within the parent.
                            iface = parent.gc["cgraph"][node.iam + "d"]
                            assert iface is not None, "Interface cannot be None."
                            src.row, src.idx = unpack_src_ref(iface[src.idx].refs[0])
                            if src.row in (SrcRow.I, SrcRow.S, SrcRow.L, SrcRow.W):
                                src.node = parent
                                node = parent
                                # If the source in the parent is row I & its parent is the root
                                # then the source is terminal - it is a connection to the top level
                                # GC input interface.
                                src.terminal = parent.terminal or node is NULL_GC_NODE
                                # If the new src node (original parent) is not terminal then
                                # just continue to the next iteration.
                                if not src.terminal:
                                    continue
                            else:
                                # If the source is not row I then then it has to be A
                                # and this node must be B
                                src.node = parent.gca_node
                                assert node is parent.gcb_node, "Node must be GCB here."
                                iface = src.node.gc["cgraph"]["Od"]
                                node = parent
                                src.terminal = src.node.terminal
                        else:
                            iface = None
                            src.terminal = True
                    case _:
                        raise ValueError(f"Invalid source row: {src.row}")
                # In all none terminal cases the new source row and index populated from the
                # c_graph connection.
                if not src.terminal:
                    assert iface is not None, "Interface cannot be None."
                    src.row, src.idx = unpack_src_ref(iface[src.idx].refs[0])
                elif src.node.is_meta and not self.wmc:
                    # Meta-codons are not being written so a bypass has to be engineered.
                    # A requirement of meta codons is that they are "straight through" i.e.
                    # inputs map directly to outputs so we can fake it.
                    src.row = SrcRow.I
                    src.terminal = False
                    assert len(src.node.gc["cgraph"]["Is"]) == len(
                        src.node.gc["cgraph"]["Od"]
                    ), "Meta-codons must have matching input/output interfaces."
                    # src.idx stays the same.
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
                    # Special case: If the source node is a codon AND it's the root, we don't
                    # need to traverse further. For non-root codons, we still need to create
                    # connections to their inputs from the parent.
                    if src.node not in visited_nodes and not (
                        src.node.is_codon and src.node is root
                    ):
                        visited_nodes.add(src.node)
                        connection_stack.extend(code_connection_from_iface(node, src.node.iam))
            else:
                assert False, "Source must not be terminal."

            # If this node is conditional a connection to row F must be made
            if node is not NULL_GC_NODE and node.f_connection:
                node.f_connection = False
                # Get the source reference from the first endpoint in Fd interface
                f_ep = node.gc["cgraph"]["Fd"][0]
                f_src_row, f_src_idx = unpack_src_ref(f_ep.refs[0])
                connection_stack.append(
                    CodeConnection(
                        CodeEndPoint(node, f_src_row, f_src_idx),
                        CodeEndPoint(node, DstRow.F, 0, True),
                    )
                )

        # Return the original node with the connections made
        return root

    def code_lines(self, root: GCNode, fwconfig: FWConfig) -> list[str]:
        """Return the code lines for the GC function.
        First list are the function lines.
        """
        if not root.write:
            return []

        # Doc string lines are at the top of the function are done first
        # then the actual code lines.
        code: list[str] = [] if fwconfig.lean else self.docstring(fwconfig, root)
        ovns: list[str] = self.name_connections(root)

        # Apply optimisations
        if fwconfig.const_eval:
            self.constant_evaluation(root)
        if fwconfig.cse:
            self.common_subexpression_elimination(root)
        if fwconfig.simplification:
            self.simplification(root)
        if fwconfig.result_cache:
            # TODO: Add condition to check if the GC is eligible for caching
            self.result_cache(root)

        # Check if this is a conditional GC and route to specialized handler
        if root.is_conditional:
            return code + self._generate_conditional_function_code(root, fwconfig, ovns)

        # Check if this is a loop GC and route to specialized handler
        if root.is_loop:
            return code + self._generate_loop_function_code(root, fwconfig, ovns)

        # Write a line for each terminal node that has lines to write in the graph
        # Meta codons have 0 lines when self.wmc (write meta-codons) is false
        # Special case: If the root is a codon, it needs to be written as it IS the function body
        for node in (
            tn
            for tn in GCNodeCodeIterable(root)
            if tn.terminal and tn.num_lines and (tn is not root or root.is_codon)
        ):
            scmnt = f"  # Sig: ...{node.gc['signature'].hex()[-8:]}" if fwconfig.inline_sigs else ""
            code.append(self.inline_cstr(root=root, node=node) + scmnt)

        # Add a return statement if the function has outputs
        if len(root.gc["outputs"]) > 0:
            code.append(f"return {', '.join(ovns)}")
        return code

    def common_subexpression_elimination(self, root: GCNode) -> None:
        """Apply common subexpression elimination to the GC function.
        This optimisations identifies code paths that have identical expressions
        and replaces them with a single expression that is assigned to a variable.
        """

    def _generate_conditional_function_code(
        self, root: GCNode, fwconfig: FWConfig, ovns: list[str]
    ) -> list[str]:
        """Generate complete conditional function code for IF_THEN or IF_THEN_ELSE graphs.

        This handles conditional graph types by:
        1. Evaluating the condition (Row F)
        2. Generating if/else branches with proper code placement
        3. Assigning outputs appropriately

        Args:
            root: The conditional GC node (must be IF_THEN or IF_THEN_ELSE)
            fwconfig: Function writing configuration
            ovns: Output variable names

        Returns:
            List of code lines implementing the conditional structure
        """
        code: list[str] = []
        rtc: list[CodeConnection] = root.terminal_connections

        # Step 1: Find and handle condition variable (Row F)
        condition_conn = next((c for c in rtc if c.dst.row == DstRow.F), None)
        if condition_conn is None:
            raise ValueError(
                f"Conditional GC missing Row F connection: {root.gc['signature'].hex()}"
            )

        condition_var = condition_conn.var_name

        # Step 2: Get Row O and Row P connections
        # Row O connections define outputs when condition is TRUE
        # Row P connections define outputs when condition is FALSE
        o_connections = [c for c in rtc if c.dst.row == DstRow.O and c.dst.node is root]
        p_connections = [c for c in rtc if c.dst.row == DstRow.P and c.dst.node is root]

        # Step 3: Categorize all nodes into execution paths
        # For conditional graphs, we need to determine which nodes belong to:
        # - TRUE path (nodes that feed into Row O)
        # - FALSE path (nodes that feed into Row P)
        # - SHARED path (nodes used by both or for condition)

        # Build dependency graph: which nodes feed into Row O and Row P
        def get_dependent_nodes(connections: list[CodeConnection]) -> set[GCNode]:
            """Get all nodes that are dependencies for the given connections."""
            nodes = set()
            work_list = [c.src.node for c in connections if c.src.node is not root]
            visited = set()

            while work_list:
                node = work_list.pop()
                if node in visited or node is root:
                    continue
                visited.add(node)
                nodes.add(node)

                # Add this node's dependencies
                for conn in rtc:
                    if conn.dst.node is node and conn.src.node is not root:
                        work_list.append(conn.src.node)

            return nodes

        o_path_nodes = get_dependent_nodes(o_connections)
        p_path_nodes = get_dependent_nodes(p_connections)

        # Condition node dependencies should execute before the if
        condition_deps = (
            get_dependent_nodes([condition_conn]) if condition_conn.src.node is not root else set()
        )

        # Step 4: Generate code before the conditional
        # This includes condition evaluation and any shared computations
        for node in condition_deps:
            if node.terminal and node.num_lines:
                scmnt = (
                    f"  # Sig: ...{node.gc['signature'].hex()[-8:]}" if fwconfig.inline_sigs else ""
                )
                code.append(self.inline_cstr(root=root, node=node) + scmnt)

        # Step 5: Generate true path code (when condition is TRUE)
        true_code: list[str] = []

        # Only include nodes that are in O path but not in condition deps
        true_only_nodes = o_path_nodes - condition_deps
        for node in GCNodeCodeIterable(root):
            if node in true_only_nodes and node.terminal and node.num_lines:
                scmnt = (
                    f"  # Sig: ...{node.gc['signature'].hex()[-8:]}" if fwconfig.inline_sigs else ""
                )
                true_code.append(self.inline_cstr(root=root, node=node) + scmnt)

        # Assign outputs from Row O connections (skip self-assignments)
        for conn in o_connections:
            output_idx = conn.dst.idx
            if ovns[output_idx] != conn.var_name:
                true_code.append(f"{ovns[output_idx]} = {conn.var_name}")

        # Step 6: Generate false path code (when condition is FALSE)
        false_code: list[str] = []

        if root.graph_type == CGraphType.IF_THEN_ELSE:
            # IF_THEN_ELSE: Execute GCB
            # Only include nodes that are in P path but not in condition deps
            false_only_nodes = p_path_nodes - condition_deps
            for node in GCNodeCodeIterable(root):
                if node in false_only_nodes and node.terminal and node.num_lines:
                    scmnt = (
                        f"  # Sig: ...{node.gc['signature'].hex()[-8:]}"
                        if fwconfig.inline_sigs
                        else ""
                    )
                    false_code.append(self.inline_cstr(root=root, node=node) + scmnt)

            # Assign outputs from Row P connections (skip self-assignments)
            for conn in p_connections:
                output_idx = conn.dst.idx
                if ovns[output_idx] != conn.var_name:
                    false_code.append(f"{ovns[output_idx]} = {conn.var_name}")
        else:
            # IF_THEN: Passthrough assignments from Row P (skip self-assignments)
            for conn in p_connections:
                output_idx = conn.dst.idx
                if ovns[output_idx] != conn.var_name:
                    false_code.append(f"{ovns[output_idx]} = {conn.var_name}")

        # Step 7: Generate if/else structure with proper indentation
        code.append(f"if {condition_var}:")
        # Ensure we have at least one line in the if block
        if true_code:
            for line in true_code:
                code.append(f"\t{line}")
        else:
            code.append("\tpass")

        code.append("else:")
        # Ensure we have at least one line in the else block
        if false_code:
            for line in false_code:
                code.append(f"\t{line}")
        else:
            code.append("\tpass")

        # Step 8: Return statement (outside the if/else)
        if len(root.gc["outputs"]) > 0:
            code.append(f"return {', '.join(ovns)}")

        return code

    def constant_evaluation(self, root: GCNode) -> None:
        """Apply constant evaluation to the GC function.
        This optimisations identifies code paths that always return the same result
        and replaces them with the constant result.
        """

    def create_code_graphs(self, root: GCNode, executable: bool = True) -> list[GCNode]:
        """Return the list of GCNode instances that need to be written. i.e. that need code graphs.
        If a node (function) is not yet written it has not been assigned a global index.
        The executable boolean is used to determine if the function map should be
        updated with the new function. This is used when the function map is being
        created. When a EC is being written to a file the function map is not updated but
        the code graphs must be regenerated as these are not persisted.
        """
        # The function map is used to determine if a function has already been written
        # Note that the code graph may have the same function to be written in multiple
        # places. This is because the function may be called multiple times in the same
        # top level GC function.
        nwcg: list[GCNode] = []
        for node in (ng for ng in root if ng.write):
            # Set the global index for the node in execution context
            # A node will use the same index as an identical node in the same context
            # for code reuse. Naming must happen before the function is defined.
            if node.gc["signature"] not in self.function_map:
                self.code_graph(node)
                self.new_function_placeholder(node)
                nwcg.append(node)
            else:
                # Node that use the same function must reference the correct info
                node.finfo = self.function_map[node.gc["signature"]]

        if executable:
            for node in nwcg:
                # Define the function in the execution context. Defining the function may involve
                # calling other functions not yet defined. This is why the function must be named
                # before it is defined.
                self.new_function(node)

        return nwcg

    def create_graphs(self, gc: GCABC, executable: bool = True) -> tuple[GCNode, list[GCNode]]:
        """Create the node code graphs for the GC function."""
        root: GCNode = self.node_graph(gc)
        root.line_count(self._line_limit)
        return root, self.create_code_graphs(root, executable)

    def define(self, code: str) -> None:
        """Define a function in the execution context."""
        exec(code, self.namespace)  # pylint: disable=exec-used

    def docstring(self, fwconfig: FWConfig, root: GCNode) -> list[str]:
        """Return the docstring for the GC function."""
        dstr: list[str] = []
        open_str = '"""'
        if fwconfig.signature:
            dstr.append(f"{open_str}Signature: {root.gc['signature'].hex()}")
            open_str = ""
        if fwconfig.created:
            dstr.append(f"{open_str}Created: {root.gc['created']}")
            open_str = ""
        if fwconfig.license:
            dstr.append(f"{open_str}License: {root.gc.get('license', 'MIT')}")
            open_str = ""
        if fwconfig.creator:
            dstr.append(f"{open_str}Creator: {root.gc['creator']}")
            open_str = ""
        if fwconfig.generation:
            dstr.append(f"{open_str}Generation: {root.gc['generation']}")
            open_str = ""
        if fwconfig.version and "version" in root.gc:
            dstr.append(f"{open_str}Version: {root.gc['version']}")
            open_str = ""
        if fwconfig.optimisations:
            dstr.append(f"{open_str}Optimisations:")
            dstr.append("   - Dead code elimination: True")
            dstr.append(f"   - Constant evaluation: {fwconfig.const_eval}")
            dstr.append(f"   - Common subexpression elimination: {fwconfig.cse}")
            dstr.append(f"   - Simplification: {fwconfig.simplification}")
        if open_str:
            dstr.append('"""EGP generated Genetic Code function."""')
        else:
            dstr.append('"""')
        return dstr

    def execute(self, gcsig: bytes | GCABC, args: tuple[Any, ...]) -> Any:
        """Execute the function in the execution context."""
        signature = gcsig["signature"] if isinstance(gcsig, GCABC) else gcsig
        assert isinstance(signature, bytes), f"Invalid signature type: {type(signature)}"

        # Ensure the function is defined & get its info
        if signature not in self.function_map:
            self.write_executable(signature)
        finfo = self.function_map[signature]
        if finfo.executable is NULL_EXECUTABLE:
            raise RuntimeError(
                "Function was created with executable=False: "
                "Re-create the execution context and re-write using "
                "executable=True. You cannot patch the context."
            )

        # NB: RuntimeContext is not used if the GC is not a PGC
        rtctxt = ""
        lns: dict[str, Any] = {"i": args}
        if finfo.gc.is_pgc():
            # TODO: Need to pass in creator info here
            lns["rtctxt"] = RuntimeContext(self.gpi, finfo.gc)
            rtctxt = "rtctxt, "

        execution_str = f"result = {finfo.name()}({rtctxt}{'i' if args else ''})"
        exec(execution_str, self.namespace, lns)  # pylint: disable=exec-used
        return lns["result"]

    def function_def(self, node: GCNode, fwconfig: FWConfig = FWCONFIG_DEFAULT) -> str:
        """Create the function definition in the execution context including the imports."""
        code = self.code_lines(node, fwconfig)
        fstr = node.function_def(fwconfig.hints)
        code.insert(0, fstr)
        return "\n\t".join(code)

    def inline_cstr(self, root: GCNode, node: GCNode) -> str:
        """Return the code string for the GC inline code."""
        # By default the ovns is underscore (unused) for all outputs. This is then overridden by any connection that starts (is source endpoint) at this node.
        ngc = node.gc
        ovns: list[str] = ["_"] * len(ngc["outputs"])
        rtc: list[CodeConnection] = root.terminal_connections
        for ovn, idx in ((c.var_name, c.src.idx) for c in rtc if c.src.node is node):
            ovns[idx] = ovn

        # Similary the ivns are defined. However, they must have variable names as they
        # cannot be undefined.
        ivns: list[str] = [NULL_STR] * len(ngc["inputs"])
        # Special case: If this node is a codon and it's the root, inputs come directly
        # from the function parameter 'i', not from connections
        if node.is_codon and node is root:
            ivns = [i_cstr(i) for i in range(len(ngc["inputs"]))]
        else:
            for ivn, idx in ((c.var_name, c.dst.idx) for c in rtc if c.dst.node is node):
                ivns[idx] = ivn

        # Is this node a codon?
        assignment = ", ".join(ovns) + " = "
        if node.is_codon:
            if ngc["signature"] not in self._codon_register:
                # Only codons have imports or introduce new types (which may have imports)
                # Make sure the imports are captured
                self._codon_register.add(ngc["signature"])
                # Make an import chain
                ifc = chain(ngc["cgraph"]["Is"], ngc["cgraph"]["Od"])
                ic = chain(ngc["imports"], chain.from_iterable(t.typ.imports for t in ifc))
                # Only import what we have not already imported.
                for impt in (i for i in ic if i not in self.imports):
                    self.define(str(impt))
                    self.imports.add(impt)
            ivns_map: dict[str, str] = {f"i{i}": ivn for i, ivn in enumerate(ivns)}
            if node.is_pgc:
                ivns_map["pgc"] = "rtctxt, "
            return assignment + ngc["inline"].format_map(ivns_map)
        return assignment + node.finfo.call_str(ivns)

    def line_limit(self) -> int:
        """Return the maximum number of lines in a function."""
        return self._line_limit

    def name_connections(self, root: GCNode) -> list[str]:
        """Name the source variable of the connection between two code endpoints."""

        # Gather the output variable names to catch the case where an input is
        # directly connected to an output
        _ovns: list[str] = ["" for _ in range(len(root.gc["outputs"]))]
        root.terminal_connections.sort(key=connection_key)
        src_connection_map: dict[CodeEndPoint, CodeConnection] = {}
        for connection in root.terminal_connections:
            dst: CodeEndPoint = connection.dst
            # If the code for this function is being regenerated then the
            # connections have already been named, but we still need to
            # make sure the return
            if connection.var_name is NULL_STR:
                # Quick reference the source code endpoint,
                # the output variable names and the output index
                src: CodeEndPoint = connection.src
                idx: int = src.idx

                # If the source endpoint already has a variable name assigned
                # from another connection then this connection must use that name.
                if src in src_connection_map:
                    connection.var_name = src_connection_map[src].var_name
                    continue
                src_connection_map[src] = connection

                # Priority naming is given to input and output variables
                # This keeps all inputs as ix and outputs as ox except in the
                # case where the input is directly connected to the output.
                if src.row == SrcRow.I:
                    assert src.node is root, "Invalid connection source node."
                    assert connection.var_name == "", "Input variable name already assigned."
                    connection.var_name = i_cstr(idx)
                elif (
                    dst.row == DstRow.O or dst.row == DstRow.P
                ) and connection.var_name is NULL_STR:
                    assert dst.node is root, "Invalid connection destination node."
                    connection.var_name = o_cstr(dst.idx)
                elif connection.var_name is NULL_STR:
                    assert src.row in (
                        SrcRow.A,
                        SrcRow.B,
                        SrcRow.S,
                        SrcRow.L,
                        SrcRow.W,
                    ), "Invalid source row."
                    number = next(root.local_counter)
                    connection.var_name = t_cstr(number)
                else:
                    raise ValueError("Invalid connection source row.")

            # Gather the outputs for this node (may not be named ox if connected to an input)
            if dst.row == DstRow.O or dst.row == DstRow.P:
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
        node.finfo = newf
        return newf

    def new_function(self, node: GCNode) -> FunctionInfo:
        """Create a new function in the execution context."""
        code = self.function_def(node)

        # Debugging
        if _logger.isEnabledFor(DEBUG):
            _logger.log(DEBUG, "Function:\n%s", node.finfo.name())
            _logger.log(DEBUG, "Code:\n%s", code)

        # Add to the execution context
        self.define(code)
        node.finfo.executable = self.namespace[node.finfo.name()]
        return node.finfo

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
        node_stack: list[GCNode] = [
            gc_node_graph := GCNode(gc, None, SrcRow.I, finfo, gpi=self.gpi, wmc=self.wmc)
        ]

        # Define the GCNode data
        while node_stack:
            # See [Assessing a GC for Function Creation](docs/executor.md) for more information.
            node: GCNode = node_stack.pop(0)
            # if _LOG_DEBUG:
            # _logger.debug("Assessing node: %s", node)
            if node.is_codon or node.unknown:
                continue
            child_nodes = ((DstRow.A, node.gca), (DstRow.B, node.gcb))
            for row, xgc in (x for x in child_nodes if x[1] is not NULL_GC):
                assert isinstance(xgc, GCABC), "GCA or GCB must be a GCABC instance"
                fmap = self.function_map.get(xgc["signature"], NULL_FUNCTION_MAP)
                gc_node_graph_entry: GCNode = GCNode(
                    xgc, node, row, fmap, gpi=self.gpi, wmc=self.wmc
                )
                if row == DstRow.A:
                    node.gca_node = gc_node_graph_entry
                else:
                    node.gcb_node = gc_node_graph_entry
                assert (
                    fmap.line_count <= self._line_limit
                ), f"# lines in function exceeds limit: {fmap.line_count} > {self._line_limit}"

                # If the function does not have a global index then it is not yet defined
                # Note that the global index is used rather than a check of whether the executable
                # is NULL_EXECUTABLE because when writing the execution context to a fiel
                # the node (and code)
                # graphs must be regenerated but we do not need the executables which a) takes time
                # and b) uses a lot of memory needlessly.
                if fmap.global_index != -1:
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
                        gc_node_graph_entry.finfo.line_count = 1
                        gc_node_graph_entry.num_lines = 1
                else:
                    node_stack.append(gc_node_graph_entry)
        return gc_node_graph

    def result_cache(self, root: GCNode) -> None:
        """Apply result caching to the GC function.
        This optimisations uses the functools lru_cache to cache the results of the function.
        The cache is only applied if the GC is eligible for caching.
        """
        # Note: This is a placeholder for future implementation
        # Need to figure out how to profile & resource manage the cache.
        # Thoughts: Cache size is a function of usage & memory available.

    def simplification(self, root: GCNode) -> None:
        """Apply simplification to the GC function.
        This optimisations uses symbolic regression to simplify the code.
        """

    def write_executable(self, gc: GCABC | bytes, executable: bool = True) -> GCNode | None:
        """Write the code for the GC.

        Sub-GC's are looked up in the gc_store.
        The returned lists are the imports and functions.
        Note that functions will be between limit/2 and limit lines long.

        1. Graph bi-directional graph of GC's

        Args:
            gc (GCABC | bytes): The Genetic Code.
            executable (bool): Creates an in memory executable of the GC when True. False
                is typically used for writing out the execution context to a file.

        Returns:
            GCNode: The GC node graph or None if the GC already exists as a suitable function.
        """
        sig: bytes = gc["signature"] if isinstance(gc, GCABC) else gc
        assert isinstance(sig, bytes), f"Invalid signature type: {type(sig)}"

        # Function already exists & is a reasonable size
        if sig in self.function_map and self.function_map[sig].line_count > self._line_limit // 2:
            return None

        # The GC may have been assessed as part of another GC but not an executable in its own right
        # The GC node graph is needed to determine connectivity and so we reset the num_lines
        # and re-assess
        _gc: GCABC = gc if isinstance(gc, GCABC) else self.gpi[sig]
        root, _ = self.create_graphs(_gc, executable)
        return root

    def _generate_loop_function_code(
        self, root: GCNode, fwconfig: FWConfig, ovns: list[str]
    ) -> list[str]:
        """Generate complete loop function code for FOR_LOOP or WHILE_LOOP graphs.

        This handles loop graph types by:
        1. Initializing loop state and condition/iterable
        2. Generating the loop structure (for/while)
        3. Generating the loop body code
        4. Handling implicit feedback (next state -> current state)
        5. Assigning outputs appropriately

        Args:
            root: The loop GC node (must be FOR_LOOP or WHILE_LOOP)
            fwconfig: Function writing configuration
            ovns: Output variable names

        Returns:
            List of code lines implementing the loop structure
        """
        code: list[str] = []
        rtc: list[CodeConnection] = root.terminal_connections

        # Step 1: Identify key connections and variables
        # Loop initialization connections (from outside to loop components)
        l_conn = next((c for c in rtc if c.dst.row == DstRow.L), None)  # Iterable (For)
        w_conn = next((c for c in rtc if c.dst.row == DstRow.W), None)  # Condition (While)
        s_conn = next((c for c in rtc if c.dst.row == DstRow.S), None)  # Initial State

        if root.graph_type == CGraphType.FOR_LOOP and l_conn is None:
            raise ValueError(f"For-Loop GC missing Row L connection: {root.gc['signature'].hex()}")

        if root.graph_type == CGraphType.WHILE_LOOP and w_conn is None:
            raise ValueError(
                f"While-Loop GC missing Row W connection: {root.gc['signature'].hex()}"
            )

        # Loop body update connections (from body to next iteration)
        t_conn = next((c for c in rtc if c.dst.row == DstRow.T), None)  # Next State
        x_conn = next((c for c in rtc if c.dst.row == DstRow.X), None)  # Next Condition (While)

        # Output connections
        o_connections = [c for c in rtc if c.dst.row == DstRow.O and c.dst.node is root]
        p_connections = [c for c in rtc if c.dst.row == DstRow.P and c.dst.node is root]

        # Step 2: Determine dependencies for initialization
        # Nodes that must execute before the loop starts
        init_conns = [c for c in [l_conn, w_conn, s_conn] if c is not None]

        def get_dependent_nodes(connections: list[CodeConnection]) -> set[GCNode]:
            """Get all nodes that are dependencies for the given connections."""
            nodes = set()
            work_list = [c.src.node for c in connections if c.src.node is not root]
            visited = set()

            while work_list:
                node = work_list.pop()
                if node in visited or node is root:
                    continue
                visited.add(node)
                nodes.add(node)

                # Add this node's dependencies
                for conn in rtc:
                    if conn.dst.node is node and conn.src.node is not root:
                        work_list.append(conn.src.node)

            return nodes

        init_deps = get_dependent_nodes(init_conns)

        # Determine loop variables (Ls, Ss, Ws)
        ls_conns = [c for c in rtc if c.src.node is root and c.src.row == SrcRow.L]
        ss_conns = [c for c in rtc if c.src.node is root and c.src.row == SrcRow.S]
        ws_conns = [c for c in rtc if c.src.node is root and c.src.row == SrcRow.W]

        ls_var = ls_conns[0].var_name if ls_conns else "unused_ls"
        ss_var = ss_conns[0].var_name if ss_conns else "unused_ss"
        ws_var = ws_conns[0].var_name if ws_conns else "unused_ws"

        # Ensure loop variables are defined even if not used in body
        if root.graph_type == CGraphType.FOR_LOOP and ls_var == "unused_ls":
            ls_var = t_cstr(next(root.local_counter))

        if root.graph_type == CGraphType.WHILE_LOOP and ws_var == "unused_ws":
            ws_var = t_cstr(next(root.local_counter))

        # Step 3: Generate initialization code
        for node in GCNodeCodeIterable(root):
            if node in init_deps and node.terminal and node.num_lines:
                scmnt = (
                    f"  # Sig: ...{node.gc['signature'].hex()[-8:]}" if fwconfig.inline_sigs else ""
                )
                code.append(self.inline_cstr(root=root, node=node) + scmnt)

        # Step 4: Setup loop variables
        # State variable setup
        if s_conn and ss_var != "unused_ss":
            code.append(f"{ss_var} = {s_conn.var_name}")

        # Step 5: Generate Loop Structure
        loop_body_code: list[str] = []

        # Identify loop body nodes (everything not in init_deps)
        # Note: Some nodes might be used in both, but if they are in init_deps they are already written.
        # However, for a loop, the body is re-executed.
        # The "body" is effectively GCA.

        # We need to be careful here. The nodes in the body are those that depend on
        # Ls (Loop source), Ss (State source), or Ws (Condition source).
        # These are the inputs to the loop body.

        # Let's find the nodes that are part of the loop body execution.
        # These are nodes that are reachable from Ls, Ss, or Ws.
        # But in our graph structure, we look at terminal connections.
        # The terminal connections for the loop body are those feeding into T, X, and O.

        body_conns = [c for c in [t_conn, x_conn] if c is not None] + o_connections
        body_nodes = get_dependent_nodes(body_conns)

        # Nodes that are strictly inside the loop (depend on loop inputs)
        # vs nodes that are constant relative to the loop (calculated outside).
        # For simplicity in this implementation, we'll put all body_nodes inside the loop
        # unless they were already written in init_deps.
        # Ideally, we should only put nodes that depend on loop variables inside.

        # Generate body code
        # We iterate through nodes in topological order (GCNodeCodeIterable does this?)
        # We filter for nodes that are in `body_nodes` and not `init_deps` (unless re-eval needed?)
        # Safe bet: write all body_nodes inside loop, except those strictly constant?
        # For now, write all body_nodes inside.

        loop_nodes = (
            body_nodes  # - init_deps? If we exclude init_deps, we assume they are constant.
        )

        for node in GCNodeCodeIterable(root):
            if node in loop_nodes and node.terminal and node.num_lines:
                # Check if node was already written in init and is constant?
                # For now, just write it.
                scmnt = (
                    f"  # Sig: ...{node.gc['signature'].hex()[-8:]}" if fwconfig.inline_sigs else ""
                )
                loop_body_code.append(self.inline_cstr(root=root, node=node) + scmnt)

        # Handle Feedback / Next State
        # Update state variable: ss_var = t_conn.var_name
        if t_conn and ss_var != "unused_ss":
            loop_body_code.append(f"{ss_var} = {t_conn.var_name}")

        # Handle While Condition Update
        if root.graph_type == CGraphType.WHILE_LOOP:
            if x_conn and ws_var != "unused_ws":
                loop_body_code.append(f"{ws_var} = {x_conn.var_name}")

        # Handle Outputs (Row O)
        # Outputs in loops are often accumulations or last values.
        # If O connects from A (body), it outputs every iteration?
        # No, the function returns once.
        # If the graph implies returning a list of results, that's different.
        # Standard Python loop semantics: variables defined in loop leak out.
        # So if O connects from A, it gets the *last* value computed.
        # We don't need explicit assignment inside the loop for O,
        # unless O is a list we are appending to?
        # The EGP graph semantics for loops usually imply:
        # - O gets the value from the last iteration.
        # - Or O gets the state T?
        # The connections define it. If As -> Od, then Od gets As from last iteration.

        # Construct the loop statement
        if root.graph_type == CGraphType.FOR_LOOP:
            assert l_conn is not None
            # for ls_var in l_conn.var_name:
            code.append(f"for {ls_var} in {l_conn.var_name}:")
        else:  # WHILE_LOOP
            assert w_conn is not None
            # while ws_var:
            # But ws_var needs to be initialized.
            # It is initialized by w_conn (Is -> Wd).
            # But w_conn.var_name is the *input* to Wd.
            # ws_var is the *output* from Ws.
            # We need to initialize ws_var = w_conn.var_name
            code.append(f"{ws_var} = {w_conn.var_name}")
            code.append(f"while {ws_var}:")

        # Debugging
        # print(f"Loop Code:\n{'\n'.join(code)}")

        # Add body
        if loop_body_code:
            for line in loop_body_code:
                code.append(f"\t{line}")
        else:
            code.append("\tpass")

        # Step 6: Handle Zero Iteration / False Path (Row P)
        # If the loop didn't run (or condition initially false), we might need Row P values.
        # But Python variables from loop might be undefined if loop didn't run.
        # We need to handle this.
        # Strategy: Initialize output variables with Row P values *before* the loop?
        # Or check after loop?

        # If we init with P values:
        # o_var = p_val
        # loop...
        #   o_var = body_val
        # return o_var

        # This works if P and O target the same outputs.
        # Let's check P connections.
        for p_conn in p_connections:
            # p_conn.dst is Row P.
            # We need to find the corresponding Row O output index.
            # P and O are "alternate" interfaces for the same physical outputs.
            # So Pd[i] corresponds to Od[i].
            out_idx = p_conn.dst.idx
            # Find the variable name for this output
            out_var = ovns[out_idx]

            # Initialize it before loop
            # Only if it's not already assigned (e.g. if P connects from I, it's just a var name)
            if out_var != p_conn.var_name:
                # Insert before loop
                # We need to insert this *after* init code but *before* loop start
                code.insert(
                    len(code) - (len(loop_body_code) + 1 if loop_body_code else 2),
                    f"{out_var} = {p_conn.var_name}",
                )
            else:
                # If they are the same name, it's already "assigned"
                pass

        # Step 7: Final Assignments for Row O
        # If O connects from A (body), the variable `out_var` should have been updated in loop.
        # If we initialized it with P, and loop ran, it got overwritten.
        # If loop didn't run, it keeps P value.
        # This seems correct.

        # However, we need to ensure the loop body actually updates `out_var`.
        # In `loop_body_code`, we generated assignments to `ovns`?
        # No, `inline_cstr` generates assignments to `t_xxx` or `o_xxx`.
        # `name_connections` assigns `o_xxx` to connections targeting O.
        # So if As -> Od, the connection var_name is `o_xxx`.
        # The inline code for A will write to `o_xxx`.
        # So yes, the loop body updates the output variables directly.

        # One catch: `name_connections` might assign `o_xxx` to the connection As->Od.
        # But if As also goes to Td (As->Td), does it get a different name?
        # `name_connections` handles this:
        # "If the source endpoint already has a variable name assigned... use that name."
        # So As->Od runs first, As gets `o_xxx`. Then As->Td uses `o_xxx`.
        # So `ss_var = t_conn.var_name` becomes `ss_var = o_xxx`. Correct.

        # What if As -> Td is processed first? (key 2)
        # It gets `t_xxx`.
        # Then As -> Od uses `t_xxx`.
        # Then we need `o_xxx = t_xxx` at the end?
        # `name_connections` logic:
        # if dst.row == DstRow.O ... connection.var_name = o_cstr(dst.idx)
        # This logic is inside the loop over connections.
        # It seems it tries to force `o_cstr` if targeting O.
        # But if it already has a name?
        # "If the source endpoint already has a variable name assigned... continue"
        # So As->Td runs first, As gets `t_xxx`. As->Od sees `t_xxx` and uses it.
        # Then `_ovns[dst.idx] = connection.var_name` sets the output name to `t_xxx`.
        # This means the return statement will be `return t_xxx`.
        # This is valid! We don't strictly need `o0` variable name, just *a* variable.

        # So, the logic holds.

        # Step 8: Return statement (outside the loop)
        if len(root.gc["outputs"]) > 0:
            code.append(f"return {', '.join(ovns)}")

        return code
