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

from collections.abc import ItemsView, Iterator, KeysView, Mapping, ValuesView
from pprint import pformat
from typing import Any

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.object_deduplicator import ObjectDeduplicator
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_abc import FrozenCGraphABC
from egppy.genetic_code.c_graph_constants import (
    _UNDER_DST_KEY_DICT,
    _UNDER_KEY_DICT,
    _UNDER_ROW_CLS_INDEXED,
    _UNDER_SRC_KEY_DICT,
    IFKEY_ROW_MAP,
    IMPLY_P_IFKEYS,
    ROW_CLS_INDEXED_ORDERED,
    ROW_CLS_INDEXED_SET,
    DstIfKey,
    DstRow,
    IfKey,
    JSONCGraph,
    Row,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.endpoint_abc import EndpointMemberType
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.frozen_ep_ref import FrozenEPRef, FrozenEPRefs
from egppy.genetic_code.frozen_interface import DESTINATION_ROW_SET, SOURCE_ROW_SET, FrozenInterface
from egppy.genetic_code.interface import ROW_SET
from egppy.genetic_code.interface_abc import FrozenInterfaceABC, InterfaceABC
from egppy.genetic_code.json_cgraph import (
    CGT_VALID_DST_ROWS,
    CGT_VALID_ROWS,
    CGT_VALID_SRC_ROWS,
    c_graph_type,
)
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Deduplication stores
type_tuple_store: ObjectDeduplicator = ObjectDeduplicator("Type Tuple", 2**14)
src_refs_store: ObjectDeduplicator = ObjectDeduplicator("Source Reference Tuple", 2**14)
refs_store: ObjectDeduplicator = ObjectDeduplicator("Reference Tuple", 2**11)
frozen_cgraph_store: ObjectDeduplicator = ObjectDeduplicator("Frozen CGraph", 2**12)


class FrozenCGraph(FrozenCGraphABC, CommonObj):
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

    __slots__ = _UNDER_ROW_CLS_INDEXED + ("_hash",)

    def __init__(
        self,
        graph: (
            Mapping[IfKey, list[EndpointMemberType]]
            | Mapping[IfKey, FrozenInterfaceABC]
            | FrozenCGraphABC
        ),
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
        assert (
            any(key in graph for key in ROW_CLS_INDEXED_ORDERED) or not graph
        ), "Input graph not empty but contains no valid interface keys."
        for key in ROW_CLS_INDEXED_ORDERED:
            row = IFKEY_ROW_MAP[key]
            _key = _UNDER_KEY_DICT[key]
            if key in graph:
                iface = graph[key]
                if isinstance(iface, InterfaceABC):
                    type_tuple = type_tuple_store[tuple(ep.typ for ep in iface)]
                    con_tuple = tuple(
                        src_refs_store[
                            tuple(
                                refs_store[
                                    (
                                        ep.refs
                                        if isinstance(ep.refs, FrozenEPRefs)
                                        else FrozenEPRefs(
                                            tuple(FrozenEPRef(r.row, r.idx) for r in ep.refs)
                                        )
                                    )
                                ]
                                for ep in iface
                            )
                        ]
                    )
                else:
                    assert isinstance(iface, list), "Interface must be a list of EndpointMemberType"
                    type_tuple = type_tuple_store[tuple(ep[3] for ep in iface)]
                    con_tuple = tuple(
                        src_refs_store[
                            tuple(
                                refs_store[
                                    FrozenEPRefs(
                                        tuple(FrozenEPRef(r[0], r[1]) for r in ep[4])  # type ignore
                                    )
                                ]
                                for ep in iface
                            )
                        ]
                    )
                fiface = (
                    iface
                    if type(iface) is FrozenInterface  # pylint: disable=unidiomatic-typecheck
                    else FrozenInterface(row, type_tuple, con_tuple)
                )
                setattr(self, _key, fiface)
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

    def __contains__(self, key: object) -> bool:
        """Check if the interface exists in the Connection Graph.

        Args:
            key: Interface identifier, may be a row or row with class postfix.

        Returns:
            True if the interface exists, False otherwise.

        Raises:
            KeyError: If the key is not a valid interface identifier.
        """
        assert isinstance(key, str), f"Key must be a string, got {type(key)}"
        if len(key) == 1:
            exists = False
            if key not in ROW_SET:
                raise KeyError(f"Invalid Connection Graph key: {key}")
            if key in DESTINATION_ROW_SET:
                exists = getattr(self, _UNDER_DST_KEY_DICT[key]) is not None
            if key in SOURCE_ROW_SET:
                exists = exists or getattr(self, _UNDER_SRC_KEY_DICT[key]) is not None
            return exists
        if key not in ROW_CLS_INDEXED_SET:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        return getattr(self, _UNDER_KEY_DICT[key]) is not None

    def __copy__(self):
        """Called by copy.copy()"""
        return self

    def __deepcopy__(self, memo):
        """
        Called by copy.deepcopy().
        'memo' is a dictionary used to track recursion loops.
        """
        # Since we are returning self, we don't need to use memo,
        # but the signature requires it.
        return self

    def __eq__(self, value: object) -> bool:
        """Check equality of Connection Graphs.
        This implements deep equality checking between two Connection Graph instances
        which can be quite expensive for large graphs.
        """
        if not isinstance(value, FrozenCGraphABC):
            return False
        if len(self) != len(value):
            return False
        if not all(key in value for key in self):
            return False
        return all(a == b for a, b in zip(self.values(), value.values()))

    def __getitem__(self, key: IfKey) -> FrozenInterfaceABC:
        """Get the interface with the given key."""
        if key not in ROW_CLS_INDEXED_SET:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        value = getattr(self, _UNDER_KEY_DICT[key])
        if value is None:
            raise KeyError(f"Connection Graph key not set: {key}")
        return value

    def __hash__(self) -> int:
        """Return the hash of the Connection Graph.

        Returns:
            Pre-computed hash value for the frozen graph.
        """
        return self._hash

    def __iter__(self) -> Iterator[IfKey]:
        """Return an iterator over the Interfaces of the Connection Graph."""
        return (
            key
            for key in ROW_CLS_INDEXED_ORDERED
            if getattr(self, _UNDER_KEY_DICT[key]) is not None
        )

    def __len__(self) -> int:
        """Return the number of interfaces in the Connection Graph."""
        return sum(1 for key in _UNDER_ROW_CLS_INDEXED if getattr(self, key) is not None)

    def __repr__(self) -> str:
        """Return a string representation of the Connection Graph."""
        return pformat(self.to_json(), indent=4, width=120)

    def _verify_all_destinations_connected(self) -> None:
        """Verify that all destination endpoints are connected.
        This check applies to stable graphs only.
        """
        unconnected: list[str] = []
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is None:
                continue

            for ep in dst_iface:
                if not ep.is_connected():
                    unconnected.append(f"{dst_row}{ep.idx}")

        self.value_error(
            len(unconnected) == 0,
            f"Stable/frozen graph has unconnected destination endpoints: {unconnected}",
        )

    def _verify_connectivity_rules(
        self,
        graph_type: CGraphType,
        valid_src_rows_dict: Mapping[DstRow, frozenset[SrcRow]],
        valid_dst_rows_dict: Mapping[SrcRow, frozenset[DstRow]],
    ) -> None:
        """Verify that endpoint connections follow the graph type rules.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        # Check destination endpoints connect to valid source rows
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is None:
                continue

            valid_srcs = valid_src_rows_dict.get(dst_row, frozenset())
            for ep in dst_iface:
                if ep.is_connected():
                    for ref in ep.refs:
                        ref_row_str = ref.row
                        ref_idx = ref.idx
                        # Check that the source row is valid for this destination
                        self.value_error(
                            ref_row_str in valid_srcs,
                            f"Destination {dst_row}{ep.idx} connects to {ref_row_str}{ref_idx}, "
                            f"but {ref_row_str} is not a valid source for"
                            f" {dst_row} in {graph_type} graphs. "
                            f"Valid sources: {valid_srcs}",
                        )

        # Check source endpoints connect to valid destination rows
        for src_row in SrcRow:
            src_iface = getattr(self, _UNDER_SRC_KEY_DICT[src_row])
            if src_iface is None:
                continue

            valid_dsts = valid_dst_rows_dict.get(src_row, frozenset())
            for ep in src_iface:
                if ep.is_connected():
                    for ref in ep.refs:
                        ref_row_str = ref.row
                        ref_idx = ref.idx
                        # Check that the destination row is valid for this source
                        self.value_error(
                            ref_row_str in valid_dsts,
                            f"Source {src_row}{ep.idx} connects to {ref_row_str}{ref_idx}, "
                            f"but {ref_row_str} is not a valid destination for "
                            f"{src_row} in {graph_type.name} graphs. "
                            f"Valid destinations: {valid_dsts}",
                        )

    def _verify_interface_presence(
        self, graph_type: CGraphType, valid_rows_set: frozenset[Row]
    ) -> None:
        """Verify that only valid interfaces for the graph type are present.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        for key in ROW_CLS_INDEXED_ORDERED:
            iface = getattr(self, _UNDER_KEY_DICT[key])
            if iface is not None:
                # Extract the row from the key (first character)
                row_str = key[0]
                self.value_error(
                    row_str in valid_rows_set,
                    f"Interface {key} is not valid for graph type {graph_type}. "
                    f"Valid rows: {valid_rows_set}",
                )

    def _verify_single_endpoint_interfaces(self) -> None:
        """Verify that F, L, W interfaces have at most 1 endpoint.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        for row in [DstRow.F, DstRow.L, DstRow.W]:
            iface = getattr(self, _UNDER_DST_KEY_DICT[row])
            if iface is not None:
                self.value_error(
                    len(iface) <= 1,
                    f"Interface {row}d must have at most 1 endpoint, found {len(iface)}",
                )

        # L source interface must also have at most 1 endpoint
        ls_iface = getattr(self, _UNDER_SRC_KEY_DICT[SrcRow.L])
        if ls_iface is not None:
            self.value_error(
                len(ls_iface) <= 1,
                f"Interface Ls must have at most 1 endpoint, found {len(ls_iface)}",
            )

        # W source interface must also have at most 1 endpoint
        ws_iface = getattr(self, _UNDER_SRC_KEY_DICT[SrcRow.W])
        if ws_iface is not None:
            self.value_error(
                len(ws_iface) <= 1,
                f"Interface Ws must have at most 1 endpoint, found {len(ws_iface)}",
            )

    def _verify_type_consistency(self) -> None:
        """Verify that connected endpoints have matching types.
        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.
        """
        # Check all destination endpoints
        for dst_row in DstRow:
            dst_iface = getattr(self, _UNDER_DST_KEY_DICT[dst_row])
            if dst_iface is None:
                continue

            for dst_ep in dst_iface:
                if dst_ep.is_connected():
                    for ref in dst_ep.refs:
                        ref_row_str = ref.row
                        ref_idx = ref.idx
                        # Get the source endpoint
                        src_iface = getattr(self, _UNDER_SRC_KEY_DICT[ref_row_str])
                        self.value_error(
                            src_iface is not None,
                            f"Destination {dst_row}{dst_ep.idx} references non-existent"
                            f" source interface {ref_row_str}s",
                        )
                        self.value_error(
                            ref_idx < len(src_iface),
                            f"Destination {dst_row}{dst_ep.idx} references {ref_row_str}{ref_idx}, "
                            f"but {ref_row_str}s only has {len(src_iface)} endpoints",
                        )
                        src_ep = src_iface[ref_idx]
                        # Verify type consistency
                        self.value_error(
                            dst_ep.typ in types_def_store.ancestors(src_ep.typ),
                            f"Type mismatch: destination endpoint {dst_row}{dst_ep.idx} "
                            f"type '{dst_ep.typ.name}' is not compatible with source "
                            f"endpoint {ref_row_str}{ref_idx} type '{src_ep.typ.name}'",
                        )

    def get(
        self, key: IfKey, default: FrozenInterfaceABC | None = None
    ) -> FrozenInterfaceABC | None:
        """Get the interface with the given key, or return default if not found.
        NOTE: This method does not raise KeyError if key is not a valid interface key.
        """
        return getattr(self, _UNDER_KEY_DICT[key], default)

    def graph_type(self) -> CGraphType:
        """Identify and return the type of this connection graph."""
        return c_graph_type(self)

    def items(self) -> ItemsView[IfKey, FrozenInterfaceABC]:
        """Return a view of the items in the Connection Graph."""
        return ItemsView(self)

    def keys(self) -> KeysView[IfKey]:
        """Return a view of the keys in the Connection Graph."""
        return KeysView(self)

    def to_json(self, json_c_graph: bool = False) -> dict[str, Any] | JSONCGraph:
        """Convert the Connection Graph to a JSON-compatible dictionary.

        IMPORTANT: The JSON representation produced by this method is
        guaranteed to be in a consistent format and order. This is crucial
        for ensuring that hash values computed from the JSON representation
        are stable and reproducible across different runs and environments.
        The method systematically processes each interface in a predefined
        order, and constructs the JSON dictionary in a consistent manner.
        """
        jcg: dict = {}
        row_u = []
        for key in DstRow:  # This order is important for consistent JSON output
            iface: FrozenInterfaceABC = getattr(self, _UNDER_DST_KEY_DICT[key])
            if iface is not None:
                jcg[str(key) if json_c_graph else key] = iface.to_json(json_c_graph=json_c_graph)
        for key in SrcRow:  # This order is important for consistent JSON output
            iface: FrozenInterfaceABC = getattr(self, _UNDER_SRC_KEY_DICT[key])
            if iface is not None and len(iface) > 0:
                unconnected_srcs = [ep for ep in iface if not ep.is_connected()]
                row_u.extend([str(ep.row), ep.idx, ep.typ.name] for ep in unconnected_srcs)
        if json_c_graph and row_u:
            jcg["U"] = row_u
        return jcg

    def values(self) -> ValuesView[FrozenInterfaceABC]:
        """Return a view of the values in the Connection Graph."""
        return ValuesView(self)

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
                ref_key = (str(ref.row), int(ref.idx))
                if ref_key not in dst_ep_map:
                    raise ValueError(
                        f"Source endpoint {row}[{idx}] references "
                        f"{ref.row}[{ref.idx}] which does not exist"
                    )
                ref_ep = dst_ep_map[ref_key]
                # Check if the reference is bidirectional
                back_ref = (row, idx)
                found = False
                for r in ref_ep.refs:
                    if (str(r.row), int(r.idx)) == back_ref:
                        found = True
                        break
                if not found:
                    raise ValueError(
                        f"Source endpoint {row}[{idx}] references {ref.row}[{ref.idx}] "
                        f"but destination {ref.row}[{ref.idx}] does not reference back"
                    )

        # Destination endpoints reference source endpoints
        for (row, idx), ep in dst_ep_map.items():
            for ref in ep.refs:
                ref_key = (str(ref.row), int(ref.idx))
                if ref_key not in src_ep_map:
                    raise ValueError(
                        f"Destination endpoint {row}[{idx}] references"
                        f" {ref.row}[{ref.idx}] which does not exist"
                    )
                ref_ep = src_ep_map[ref_key]
                # Check if the reference is bidirectional
                back_ref = (row, idx)
                found = False
                for r in ref_ep.refs:
                    if (str(r.row), int(r.idx)) == back_ref:
                        found = True
                        break
                if not found:
                    raise ValueError(
                        f"Destination endpoint {row}[{idx}] references {ref.row}[{ref.idx}] "
                        f"but source {ref.row}[{ref.idx}] does not reference back"
                    )

        # Verify hash consistency
        # Must iterate the same way as __init__ does (using self.values())
        recomputed_hash = hash(tuple(hash(iface) for iface in self.values()))
        if self._hash != recomputed_hash:
            raise ValueError(
                f"Hash inconsistency: stored hash {self._hash} does not match "
                f"recomputed hash {recomputed_hash}"
            )

    # Graph State Methods

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable.

        A stable graph has all destination endpoints connected to source endpoints.
        Frozen graphs are guaranteed to be stable.

        Returns:
            True (always, since frozen graphs are stable by definition).
        """
        return True

    def verify(self) -> None:
        """Verify the Connection Graph structure and connectivity rules.

        CGraph is a mutable connection graph class that may be stable or unstable.
        Verification must pass for both stable and unstable graphs.

        This method validates:
        - All interfaces are properly typed
        - Graph type identification is consistent
        - Interface presence matches graph type rules
        - Endpoint connectivity follows graph type rules
        - Type consistency across connections
        - Reference validity (endpoints reference existing endpoints)

        For stable graphs (frozen or explicitly stable):
        - All destination endpoints must be connected
        - All connections must follow the graph type rules

        For unstable graphs:
        - Connections are validated but may be incomplete

        Raises:
            ValueError: If any validation check fails.
            TypeError: If any type check fails.
        """
        # Verify all interfaces
        for key in _UNDER_ROW_CLS_INDEXED:
            iface = getattr(self, key)
            if iface is not None:
                self.type_error(
                    isinstance(iface, FrozenInterfaceABC),
                    f"Interface {key} must be an Interface, got {type(iface)}",
                )
                if len(iface) > 0:
                    self.value_error(
                        iface[0].row == key[1],
                        f"Interface {key} first endpoint row must match key row "
                        f" {key[1]}, got {iface[0].row}",
                    )
                iface.verify()

        # Identify the graph type
        graph_type = c_graph_type(self)

        # Get valid rows for this graph type
        valid_rows_set = CGT_VALID_ROWS[graph_type]
        valid_src_rows_dict = CGT_VALID_SRC_ROWS[graph_type]
        valid_dst_rows_dict = CGT_VALID_DST_ROWS[graph_type]

        # Verify interfaces present match graph type rules
        self._verify_interface_presence(graph_type, valid_rows_set)

        # Verify endpoint connectivity rules
        self._verify_connectivity_rules(graph_type, valid_src_rows_dict, valid_dst_rows_dict)

        # Verify single endpoint rules for F, L, W interfaces
        self._verify_single_endpoint_interfaces()

        # Verify type consistency across connections
        self._verify_type_consistency()

        # For frozen or explicitly stable graphs, verify all destinations are connected
        if self.is_stable():
            self._verify_all_destinations_connected()

        # Call parent verify
        # Note: We do NOT call FrozenCGraph.verify() because it enforces FrozenInterface types
        # and we use mutable Interface types.
        # We call CommonObj.verify() if it exists, but CommonObj doesn't have verify().
        # CommonObj has consistency().
        # So we are done.
