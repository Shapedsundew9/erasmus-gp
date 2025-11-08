"""
Frozen Connection Graph implementation.

This module provides a memory-efficient, immutable Connection Graph implementation
optimized for frozen (read-only) graphs. Unlike the standard CGraph which supports
both mutable and frozen states, FrozenCGraph is designed to be frozen from creation
and uses optimized data structures for reduced memory footprint.

The FrozenCGraph class is particularly useful for:
- Long-term storage of genetic code structures
- Sharing graph structures across multiple genetic codes
- Reducing memory usage in large populations
- Ensuring graph immutability guarantees
"""

from __future__ import annotations

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.egp_rnd_gen import EGPRndGen, egp_rng
from egpcommon.object_deduplicator import ObjectDeduplicator
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import (
    _UNDER_KEY_DICT,
    IMPLY_P_IFKEYS,
    ROW_CLS_INDEXED_ORDERED,
    SINGLE_CLS_INDEXED_SET,
    DstIfKey,
    DstRow,
    EndPointClass,
    EPClsPostfix,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.endpoint_abc import EndpointMemberType
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.frozen_interface import FrozenInterface
from egppy.genetic_code.interface_abc import InterfaceABC
from egppy.genetic_code.json_cgraph import (
    CGT_VALID_DST_ROWS,
    CGT_VALID_ROWS,
    CGT_VALID_SRC_ROWS,
    c_graph_type,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Deduplication stores
type_tuple_store: ObjectDeduplicator = ObjectDeduplicator("Type Tuple", 2**14)
src_refs_store: ObjectDeduplicator = ObjectDeduplicator("Source Reference Tuple", 2**14)
refs_store: ObjectDeduplicator = ObjectDeduplicator("Reference Tuple", 2**11)
frozen_cgraph_store: ObjectDeduplicator = ObjectDeduplicator("Frozen CGraph", 2**12)


class FrozenCGraph(CGraph, CommonObj):
    """Frozen Connection Graph implementation.

    This class provides an immutable, memory-efficient implementation of CGraphABC
    that is optimized for frozen graphs. It uses compact data structures and
    assumes immutability from construction, allowing for optimizations that are
    not possible with the standard mutable CGraph.

    Key characteristics:
    - Always frozen (immutable from creation)
    - Optimized memory layout using compact slots
    - Pre-computed hash for O(1) hashing
    - Efficient equality comparison
    - No mutation operations allowed

    The frozen graph is created from a dictionary of interfaces.

    A CGraph is built up from Interface objects which are inturn built from
    EndPoint objects allowing for flexible manipulation of the graph structure
    as it is created & mutated. In a FrozenCGraph, the CGraph compactly stores
    the data and VirtualInterface objects are used to provide an InterfaceABC
    interface to the underlying data.
    """

    __slots__ = ("_hash",)

    def __init__(  # pylint: disable=super-init-not-called
        self, graph: dict[str, list[EndpointMemberType]] | CGraphABC
    ) -> None:
        """Initialize the Frozen Connection Graph.

        Args:
            graph: A dictionary mapping interface keys to Interface objects.

        Raises:
            TypeError: If graph is not a dict or contains invalid interface types.
            ValueError: If graph structure violates Connection Graph rules.
        """
        # Do not call the CGraph __init__ since we are building differently
        CommonObj.__init__(self)

        # Set type tuples and connection (reference) tuples for all interfaces
        # Interfaces are stored as
        #   tuple[TypesDef, ...]
        # References are stored as
        #   tuple[tuple[tuple[Row, idx], ...], ...]
        for key in ROW_CLS_INDEXED_ORDERED:
            _key = _UNDER_KEY_DICT[key]
            if key in graph:
                if isinstance(graph, CGraphABC):
                    type_tuple = tuple(ep.typ for ep in graph[key])
                    con_tuple = tuple(
                        src_refs_store[tuple(refs_store[tuple(ref)] for ref in ep.refs)]
                        for ep in graph[key]
                    )
                else:
                    type_tuple = tuple(type_tuple_store[ep[3]] for ep in graph[key])
                    con_tuple = tuple(
                        src_refs_store[tuple(refs_store[tuple(ref)] for ref in ep[4])]
                        for ep in graph[key]
                    )
                epcls = EndPointClass.SRC if key[1] == "s" else EndPointClass.DST
                row = DstRow(key[0]) if epcls == EndPointClass.DST else SrcRow(key[0])
                setattr(self, _key, FrozenInterface(row, epcls, type_tuple, con_tuple))
            elif key in (SrcIfKey.IS, DstIfKey.OD):
                # Is and Od must exist even if empty
                setattr(self, _key, [])  # Empty interface
            else:
                setattr(self, _key, None)

        # Special cases for JSONCGraphs
        # Ensure PD exists if LD, WD, or FD exist and OD is empty
        need_p = any(getattr(self, _UNDER_KEY_DICT[key]) is not None for key in IMPLY_P_IFKEYS)
        if need_p and len(getattr(self, _UNDER_KEY_DICT[DstIfKey.OD])) == 0:
            setattr(self, _UNDER_KEY_DICT[DstIfKey.PD], [])

        # Pre-compute the hash for the frozen graphs
        # For consistency, we use the same hash calculation as unfrozen graphs
        self._hash = hash(tuple(hash(iface) for iface in self.values()))

    # Container Protocol Methods (from Collection)

    def __setitem__(self, key: str, value: InterfaceABC) -> None:
        """Set the interface with the given key.

        Args:
            key: Interface identifier.
            value: Interface object to set.

        Raises:
            RuntimeError: Always raises since frozen graphs are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Connection Graph")

    def __delitem__(self, key: str) -> None:
        """Delete the interface with the given key.

        Args:
            key: Interface identifier.

        Raises:
            RuntimeError: Always raises since frozen graphs are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Connection Graph")

    def __hash__(self) -> int:
        """Return the hash of the Connection Graph.

        Returns:
            Pre-computed hash value for the frozen graph.
        """
        return self._hash

    # Graph State Methods

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable.

        A stable graph has all destination endpoints connected to source endpoints.
        Frozen graphs are guaranteed to be stable.

        Returns:
            True (always, since frozen graphs are stable by definition).
        """
        return True

    # Connection Management Methods

    def connect_all(self, if_locked: bool = True, rng: EGPRndGen = egp_rng) -> None:
        """Connect all unconnected destination endpoints to valid source endpoints.

        Args:
            if_locked: Ignored for frozen graphs.
            rng: Ignored for frozen graphs.

        Raises:
            RuntimeError: Always raises since frozen graphs cannot be modified.
        """
        raise RuntimeError("Cannot modify a frozen Connection Graph")

    def stabilize(self, if_locked: bool = True) -> None:
        """Stabilize the graph by connecting all unconnected destinations.

        Args:
            if_locked: Ignored for frozen graphs.

        Raises:
            RuntimeError: Always raises since frozen graphs cannot be modified.
        """
        raise RuntimeError("Cannot modify a frozen Connection Graph")

    # Validation Methods (from CommonObjABC)

    def consistency(self) -> None:
        """Check the consistency of the FrozenCGraph.

        Validates internal consistency such as:
        - All interfaces pass their consistency checks
        - Bidirectional reference consistency (if A references B, B must reference A)
        - Hash consistency

        Raises:
            ValueError: If consistency checks fail.
        """
        # Verify all interfaces pass consistency checks
        for key in ROW_CLS_INDEXED_ORDERED:
            if key in self:
                iface = self[key]
                iface.consistency()

        # Verify bidirectional reference consistency
        # Build separate maps for source and destination endpoints by (row, idx)
        src_ep_map: dict[tuple[str, int], FrozenEndPoint] = {}
        dst_ep_map: dict[tuple[str, int], FrozenEndPoint] = {}

        for key in ROW_CLS_INDEXED_ORDERED:
            if key in self:
                iface = self[key]
                # Determine if this is a source or destination interface
                is_src = key[1] == "s"
                target_map = src_ep_map if is_src else dst_ep_map
                for ep in iface:
                    target_map[(str(ep.row), ep.idx)] = ep  # type: ignore

        # Check that all references are bidirectional
        # Source endpoints reference destination endpoints
        for (row, idx), ep in src_ep_map.items():
            for ref in ep.refs:
                ref_key = (str(ref[0]), int(ref[1]))
                if ref_key not in dst_ep_map:
                    raise ValueError(
                        f"Source endpoint {row}[{idx}] references "
                        f"{ref[0]}[{ref[1]}] which does not exist"
                    )
                ref_ep = dst_ep_map[ref_key]
                # Check if the reference is bidirectional
                back_ref = (row, idx)
                found = False
                for r in ref_ep.refs:
                    if (str(r[0]), int(r[1])) == back_ref:
                        found = True
                        break
                if not found:
                    raise ValueError(
                        f"Source endpoint {row}[{idx}] references {ref[0]}[{ref[1]}] "
                        f"but destination {ref[0]}[{ref[1]}] does not reference back"
                    )

        # Destination endpoints reference source endpoints
        for (row, idx), ep in dst_ep_map.items():
            for ref in ep.refs:
                ref_key = (str(ref[0]), int(ref[1]))
                if ref_key not in src_ep_map:
                    raise ValueError(
                        f"Destination endpoint {row}[{idx}] references"
                        f" {ref[0]}[{ref[1]}] which does not exist"
                    )
                ref_ep = src_ep_map[ref_key]
                # Check if the reference is bidirectional
                back_ref = (row, idx)
                found = False
                for r in ref_ep.refs:
                    if (str(r[0]), int(r[1])) == back_ref:
                        found = True
                        break
                if not found:
                    raise ValueError(
                        f"Destination endpoint {row}[{idx}] references {ref[0]}[{ref[1]}] "
                        f"but source {ref[0]}[{ref[1]}] does not reference back"
                    )

        # Verify hash consistency
        # Must iterate the same way as __init__ does (using self.values())
        recomputed_hash = hash(tuple(hash(iface) for iface in self.values()))
        if self._hash != recomputed_hash:
            raise ValueError(
                f"Hash inconsistency: stored hash {self._hash} does not match "
                f"recomputed hash {recomputed_hash}"
            )

    def verify(self) -> None:
        """Verify the FrozenCGraph object.

        Performs comprehensive validation including:
        - All interfaces are properly frozen
        - Graph structure follows Connection Graph rules
        - All destination endpoints are connected (frozen graphs are always stable)
        - Type consistency across connections
        - Graph type rules are satisfied

        Raises:
            ValueError: If verification checks fail.
            TypeError: If type checks fail.
        """
        # Verify all interfaces
        for key in ROW_CLS_INDEXED_ORDERED:
            if key in self:
                iface = self[key]
                if not isinstance(iface, FrozenInterface):
                    raise TypeError(f"Interface {key} must be a FrozenInterface, got {type(iface)}")
                iface.verify()

        # Identify the graph type
        graph_type = c_graph_type(self)

        # Get valid rows for this graph type
        valid_rows_set = CGT_VALID_ROWS[graph_type]
        valid_src_rows_dict = CGT_VALID_SRC_ROWS[graph_type]
        valid_dst_rows_dict = CGT_VALID_DST_ROWS[graph_type]

        # Verify interfaces present match graph type rules
        for key in ROW_CLS_INDEXED_ORDERED:
            if key in self:
                # Extract the row from the key (first character)
                row_str = key[0]
                if row_str not in valid_rows_set:
                    raise ValueError(
                        f"Interface {key} is not valid for graph type {graph_type}. "
                        f"Valid rows: {valid_rows_set}"
                    )

        # Verify endpoint connectivity rules
        # Check destination endpoints connect to valid source rows
        for dst_row in DstRow:
            dst_key = dst_row + EPClsPostfix.DST
            if dst_key not in self:
                continue

            valid_srcs = valid_src_rows_dict.get(dst_row, frozenset())
            dst_iface = self[dst_key]
            for ep in dst_iface:
                if ep.is_connected():
                    for ref in ep.refs:
                        ref_row = ref[0]
                        if ref_row not in valid_srcs:
                            raise ValueError(
                                f"Destination endpoint {dst_row}[{ep.idx}] connects to invalid "
                                f"source row {ref_row}. Valid source rows: {valid_srcs}"
                            )

        # Check source endpoints connect to valid destination rows
        for src_row in SrcRow:
            src_key = src_row + EPClsPostfix.SRC
            if src_key not in self:
                continue

            valid_dsts = valid_dst_rows_dict.get(src_row, frozenset())
            src_iface = self[src_key]
            for ep in src_iface:
                if ep.is_connected():
                    for ref in ep.refs:
                        ref_row = ref[0]
                        if ref_row not in valid_dsts:
                            raise ValueError(
                                f"Source endpoint {src_row}[{ep.idx}] connects to invalid "
                                f"destination row {ref_row}. Valid destination rows: {valid_dsts}"
                            )

        # Verify single endpoint rules for F, L, W interfaces (when stable)

        for key in SINGLE_CLS_INDEXED_SET:
            iface = self.get(key)
            if iface is not None and len(iface) > 1:
                raise ValueError(
                    f"Interface {key} can only have 0 or 1 "
                    f"endpoints when stable, has {len(iface)}"
                )

        # Verify type consistency across connections
        # Build a map of all source endpoints by (row, idx)
        src_ep_map: dict[tuple[str, int], FrozenEndPoint] = {}
        for src_row in SrcRow:
            src_key = src_row + EPClsPostfix.SRC
            if src_key in self:
                for ep in self[src_key]:
                    src_ep_map[(ep.row, ep.idx)] = ep  # type: ignore

        # Check each destination endpoint's connection for type consistency
        for dst_row in DstRow:
            dst_key = dst_row + EPClsPostfix.DST
            if dst_key not in self:
                continue
            for dst_ep in self[dst_key]:
                if dst_ep.is_connected():
                    for ref in dst_ep.refs:
                        ref_key = (str(ref[0]), int(ref[1]))
                        if ref_key in src_ep_map:
                            src_ep = src_ep_map[ref_key]
                            if dst_ep.typ != src_ep.typ:
                                raise ValueError(
                                    f"Type mismatch: destination endpoint {dst_row}[{dst_ep.idx}] "
                                    f"type '{dst_ep.typ.name}' does not match source endpoint "
                                    f"{ref[0]}[{ref[1]}] type '{src_ep.typ.name}'"
                                )

        # Frozen graphs are always stable - verify all destinations are connected
        for dst_row in DstRow:
            dst_key = dst_row + EPClsPostfix.DST
            if dst_key not in self:
                continue
            for dst_ep in self[dst_key]:
                if not dst_ep.is_connected():
                    raise ValueError(
                        f"Frozen graph must be stable but destination endpoint "
                        f"{dst_row}[{dst_ep.idx}] is not connected"
                    )
