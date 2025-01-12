"""The Executor Module.

The classes and functions in this module support the execution of Genetic Codes.
See [The Genetic Code Executor](docs/executor.md) for more information.
"""

from typing import Any

from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.gc_graph_abc import GCGraphABC
from egppy.gc_graph.typing import ROW_CLS_INDEXED, DestinationRow, SourceRow
from egppy.gc_types.gc import GCABC, NULL_GC, NULL_EXECUTABLE
from egppy.storage.cache.cache_abc import CacheABC


def _default_work(gc_store: CacheABC, gc: GCABC, parent: dict[str, Any]) -> dict[str, Any]:
    """Return the default work dictionary.

    Work dictionaries are used to build the bi-directional graph of GC's.

    Args:
        gc (GCABC): The Genetic Code.

    Returns:
        dict[str, Any]: The default work dictionary.
    """
    return {
        "gc": gc,
        "gca": gc["gca"] if isinstance(gc["gca"], GCABC) else gc_store[gc["gca"]],
        "gcb": gc["gcb"] if isinstance(gc["gcb"], GCABC) else gc_store[gc["gcb"]],
        "parent": parent,
        "assess": True,
        "write": False,  # True if ready to be written (i.e. does not exist and should)
        "exists": False,  # True if the function already exists
        # "ROW_CLS": [],  # [{work_dict, output idx}, ...] for interface connections.
        "num_lines": 0,
        # "bi_gca": will be added if gca is not NULL_GC referring to a work dictionary
        # "bi_gcb": will be added if gcb is not NULL_GC referring to a work dictionary
    }


def _bigraph(gc_store: CacheABC, gc: GCABC, limit: int) -> dict[str, Any]:
    """Build the bi-directional graph of GC's.

    The graph is a graph of work dictionaries. A work dictionary for a GC references a work
    dictionary for each of its GCA & GCB if they exist. Note that the bigraph is a representation
    of the GC implementation and so each work dictionary is an instance of a GC not a definition.
    i.e. the same GC may appear multiple times in the bigraph. This matters because each instance
    may be implemented differently depending on what other GC's are local to it in the GC structure
    graph.

    Args:
        gc_store (CacheABC): The store of GC's. GC definitions are fetched from here.
        gc (GCABC): Is the root of the bigraph.
        limit (int): The maximum number of lines per function

    Returns:
        dict[str, Any]: The bigraph entry for the root GC. See _default_work for the structure.
    """
    assert 4 <= limit <= 2**15 - 1, f"Invalid function maximum lines limit: {limit}"

    half_limit: int = limit // 2
    work_stack: list[dict[str, Any]] = [bigraph := _default_work(gc_store, gc, {})]
    while work_stack:
        # See See [Assessing a GC for Function Creation](docs/executor.md) for more information.
        work = work_stack.pop(0)
        for xgc in (x for x in (work["gca"], work["gcb"]) if x is not NULL_GC):
            bigraph_entry: dict[str, Any] = _default_work(gc_store, xgc, work)
            work["bi_gca" if "bi_gca" not in work else "bi_gcb"] = bigraph_entry
            lines = xgc["num_lines"]
            assert lines <= limit, f"Number of lines in function exceeds limit: {lines} > {limit}"
            if xgc["executable"] is not NULL_EXECUTABLE:
                assert lines > 0, f"The # lines cannot be <= 0 when there is an executable: {lines}"
                if lines < half_limit:
                    work_stack.append(bigraph_entry)
                else:
                    # Existing executable is suitable (so no need to assess or write it)
                    bigraph_entry["assess"] = False
                    bigraph_entry["exists"] = True
                    bigraph_entry["num_lines"] = lines
            else:
                work_stack.append(bigraph_entry)
        if work["gca"] is NULL_GC and work["gcb"] is NULL_GC:
            # This is a leaf GC i.e. a codon
            work["num_lines"] = 1
            work["assess"] = False
    return bigraph


def _line_count(bigraph: dict[str, Any], limit: int) -> None:
    """Calculate the best number of lines for each function and
    mark the ones that should be written. This function traverses the bigraph
    starting at the root and working down to the leaves (codons) and then
    back up to the root accumulating line counts."""
    node: dict[str, Any] = bigraph
    while node["assess"]:

        # If GCA exists and needs assessing then assess it
        bi_gca = node["bi_gca"]
        if bi_gca["assess"]:
            node = bi_gca
            continue

        # If GCB exists and needs assessing then assess it
        num_lines_gca = bi_gca["num_lines"]
        if "bi_gcb" in node:
            bi_gcb = node["bi_gcb"]
            if bi_gcb["assess"]:
                node = bi_gcb
                continue

            # If both GCA & GCB have been assessed then determine the best number of lines
            # and mark the one to be written (if it does not already exist)
            # Initialize the interface to the written function for threading connections later.
            num_lines_gcb = bi_gcb["num_lines"]
            if num_lines_gca + num_lines_gcb > limit:
                bi_gcx = bi_gcb if num_lines_gca < num_lines_gcb else bi_gca
                bi_gcx["write"] = not bi_gcx["exists"]
                gc_graph: GCGraphABC = bi_gcx["gc"]["gc_graph"]
                for rowcls in (rc for rc in ROW_CLS_INDEXED if rc in gc_graph):
                    bi_gcx[rowcls] = [None] * len(gc_graph[rowcls])
                node["num_lines"] = bi_gcx["num_lines"] + 1
        else:
            node["num_lines"] = num_lines_gca

        # Mark the node as assessed and move to the parent
        # If the parent is empty then the bigraph line count is complete
        node["assess"] = False
        if node["parent"]:
            node = node["parent"]


def _make_connections(bigraph: dict[str, Any]) -> None:
    """The inputs and outputs of each function are determined by the connections between GC's.
    This function traverses the bigraph and makes the connections between functions."""
    node: dict[str, Any] = bigraph
    connection_stack = list(enumerate(node["gc"]["gc_graph"]["Isc"]))
    while connection_stack:
        working_idx, working_refs = connection_stack.pop(0)
        connection = {"work": node, "idx": working_idx, "src_i": True}
        while working_refs:
            dst_ref: XEndPointRefABC = working_refs.pop(0)
            assert dst_ref.is_dst(), "The end point reference must be a destination."
            dst_row: SourceRow | DestinationRow = dst_ref.get_row()
            dst_idx: int = dst_ref.get_idx()
            match dst_row:
                case DestinationRow.A:
                    next_node = node["bi_gca"]
                case DestinationRow.B:
                    next_node = node["bi_gcb"]
                case DestinationRow.F:
                    node["to_f"] = connection
                    assert dst_idx == 0, "The destination index must be 0 for F."
                    continue
                case DestinationRow.O:
                    node["to_o"][dst_idx] = connection
                    continue
                case DestinationRow.P:
                    node["to_p"][dst_idx] = connection
                    continue
                case _:
                    raise ValueError(f"Invalid destination row: {dst_row}")
            if next_node["write"] or next_node["exists"]:
                # If the function is to be written or exists then add the connection
                next_node["to_i"][dst_idx] = connection
            else:
                # If the function is not to be written and does not exist then thread through
                # to the next GC
                connection_stack.append((working_idx, next_node["gc"]["gc_graph"]["Isc"][dst_idx]))


def write_gc_executable(
    gc_store: CacheABC, gc: GCABC | bytes, limit: int = 20
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
    _gc: GCABC = gc if isinstance(gc, GCABC) else gc_store[sig]

    # If the GC executable has already been written then return
    if _gc["executable"] is not NULL_EXECUTABLE:
        return [], []

    # The GC may have been assessed as part of another GC but not an executable in its own right
    # The bigraph is needed to determine connectivity and so we reset the num_lines and re-assess
    bigraph: dict[str, Any] = _bigraph(gc_store, _gc, limit)
    _line_count(bigraph, limit)
    _make_connections(bigraph)

    return [], []
