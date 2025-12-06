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

from collections.abc import ItemsView, Iterator, KeysView, ValuesView
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
    IMPLY_P_IFKEYS,
    ROW_CLS_INDEXED_ORDERED,
    ROW_CLS_INDEXED_SET,
    SINGLE_CLS_INDEXED_SET,
    DstIfKey,
    DstRow,
    EPCls,
    IfKey,
    JSONCGraph,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.endpoint_abc import EndpointMemberType
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.frozen_interface import DESTINATION_ROW_SET, SOURCE_ROW_SET, FrozenInterface
from egppy.genetic_code.interface import ROW_SET
from egppy.genetic_code.interface_abc import FrozenInterfaceABC
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
            dict[IfKey, list[EndpointMemberType]]
            | dict[IfKey, FrozenInterfaceABC]
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
            any(key in graph for key in ROW_CLS_INDEXED_ORDERED) and graph
        ), "Input graph not empty but contains no valid interface keys."
        for key in ROW_CLS_INDEXED_ORDERED:
            _key = _UNDER_KEY_DICT[key]
            if key in graph:
                iface = graph[key]
                if isinstance(iface, FrozenInterfaceABC):
                    type_tuple = tuple(ep.typ for ep in iface)
                    con_tuple = tuple(
                        src_refs_store[tuple(refs_store[tuple(ref)] for ref in ep.refs)]
                        for ep in iface
                    )
                else:
                    assert isinstance(iface, list), "Interface must be a list of EndpointMemberType"
                    type_tuple = tuple(type_tuple_store[ep[3]] for ep in iface)
                    con_tuple = tuple(
                        src_refs_store[tuple(refs_store[tuple(ref)] for ref in ep[4])]
                        for ep in iface
                    )
                epcls = EPCls.SRC if key[1] == "s" else EPCls.DST
                row = DstRow(key[0]) if epcls == EPCls.DST else SrcRow(key[0])
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
        for dst_row, dst_key in zip(DstRow, DstIfKey):
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
        for src_row, src_key in zip(SrcRow, SrcIfKey):
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
        for src_key in SrcIfKey:
            if src_key in self:
                for ep in self[src_key]:
                    src_ep_map[(ep.row, ep.idx)] = ep  # type: ignore

        # Check each destination endpoint's connection for type consistency
        for dst_row, dst_key in zip(DstRow, DstIfKey):
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
        for dst_row, dst_key in zip(DstRow, DstIfKey):
            if dst_key not in self:
                continue
            for dst_ep in self[dst_key]:
                if not dst_ep.is_connected():
                    raise ValueError(
                        f"Frozen graph must be stable but destination endpoint "
                        f"{dst_row}[{dst_ep.idx}] is not connected"
                    )
