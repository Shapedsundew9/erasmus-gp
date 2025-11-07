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

from collections.abc import Iterator
from pprint import pformat

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.egp_rnd_gen import EGPRndGen, egp_rng
from egpcommon.object_deduplicator import ObjectDeduplicator
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import (
    _UNDER_ROW_CLS_INDEXED,
    DESTINATION_ROW_SET,
    ROW_CLS_INDEXED,
    ROW_SET,
    SINGLE_ONLY_ROWS,
    SOURCE_ROW_SET,
    DstRow,
    EndPointClass,
    EPClsPostfix,
    JSONCGraph,
    Row,
    SrcRow,
)
from egppy.genetic_code.end_point_abc import EndPointABC, EndpointMemberType
from egppy.genetic_code.interface_abc import InterfaceABC
from egppy.genetic_code.json_cgraph import (
    CGT_VALID_DST_ROWS,
    CGT_VALID_ROWS,
    CGT_VALID_SRC_ROWS,
    c_graph_type,
)
from egppy.genetic_code.types_def import TypesDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Constants
# e.g. _Isc, _Bdc where c stands for connection
_UNDER_CON_CLS_INDEXED: tuple[str, ...] = tuple(row + "c" for row in _UNDER_ROW_CLS_INDEXED)
_UNDER_INDEXED = _UNDER_ROW_CLS_INDEXED + _UNDER_CON_CLS_INDEXED

# Deduplication stores
type_tuple_store: ObjectDeduplicator = ObjectDeduplicator("Type Tuple", 2**14)
src_refs_store: ObjectDeduplicator = ObjectDeduplicator("Source Reference Tuple", 2**14)
refs_store: ObjectDeduplicator = ObjectDeduplicator("Reference Tuple", 2**11)


class FrozenInterface(InterfaceABC):
    """Frozen interfaces are immutable and introspect FrozenCGraph data structures directly.

    This class provides an immutable interface implementation that stores endpoint data
    as tuples instead of lists. It creates FrozenEndPoint instances on-the-fly when accessed.

    Attributes:
        row (Row): The row identifier for all endpoints in this interface.
        epcls (EndPointClass): The endpoint class (SRC or DST) for all endpoints.
        type_tuple (tuple[TypesDef, ...]): Tuple of types for each endpoint.
        refs_tuple (tuple[tuple[tuple[Row, int], ...], ...]): Tuple of
                    reference tuples for each endpoint.
    """

    __slots__ = ("row", "epcls", "type_tuple", "refs_tuple", "_hash")

    def __init__(
        self,
        row: Row,
        epcls: EndPointClass,
        type_tuple: tuple[TypesDef, ...],
        refs_tuple: tuple[tuple[tuple[Row, int], ...], ...],
    ):
        super().__init__()
        self.row = row
        self.epcls = epcls
        self.type_tuple = type_tuple
        self.refs_tuple = refs_tuple
        # Pre-compute hash for frozen interface
        self._hash = hash((self.row, self.epcls, self.type_tuple, self.refs_tuple))

    def __getitem__(self, idx: int) -> EndPointABC:
        """Get an endpoint by index.

        Args:
            idx: The index of the endpoint to retrieve.

        Returns:
            FrozenEndPoint at the specified index.

        Raises:
            IndexError: If idx is out of range.
        """
        if idx < 0 or idx >= len(self.type_tuple):
            raise IndexError(
                f"Index {idx} out of range for interface with {len(self.type_tuple)} endpoints"
            )
        return FrozenEndPoint(
            self.row,
            idx,
            self.epcls,
            self.type_tuple[idx],
            self.refs_tuple[idx],
        )

    def __iter__(self) -> Iterator[EndPointABC]:
        """Return an iterator over the endpoints.

        Returns:
            Iterator over FrozenEndPoint objects in the interface.
        """
        for idx, typ in enumerate(self.type_tuple):
            yield FrozenEndPoint(
                self.row,
                idx,
                self.epcls,
                typ,
                self.refs_tuple[idx],
            )

    def __len__(self) -> int:
        """Return the number of endpoints in the interface.

        Returns:
            Number of endpoints in this interface.
        """
        return len(self.type_tuple)

    def __setitem__(self, idx: int, value: EndPointABC) -> None:
        """Set an endpoint at a specific index.

        Args:
            idx: The index at which to set the endpoint.
            value: The endpoint to set.

        Raises:
            RuntimeError: Always raises since frozen interfaces are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Interface")

    def __eq__(self, value: object) -> bool:
        """Check equality of FrozenInterface instances.

        Args:
            value: Object to compare with.

        Returns:
            True if equal, False otherwise.
        """
        if not isinstance(value, InterfaceABC):
            return False
        # Fast path for FrozenInterface comparison
        if isinstance(value, FrozenInterface):
            return self._hash == value._hash
        # Slow path for comparison with mutable interfaces
        if len(self) != len(value):
            return False
        return all(a == b for a, b in zip(self, value))

    def __hash__(self) -> int:
        """Return the hash of the interface.

        Returns:
            Pre-computed hash value for the frozen interface.
        """
        return self._hash

    def __str__(self) -> str:
        """Return the string representation of the interface.

        Returns:
            String representation of the interface.
        """
        return f"FrozenInterface({', '.join(str(typ) for typ in self.type_tuple)})"

    def __add__(self, other: InterfaceABC) -> InterfaceABC:
        """Concatenate two interfaces to create a new interface.

        Args:
            other: The interface to concatenate with this interface.

        Returns:
            A new FrozenInterface containing endpoints from both interfaces.

        Raises:
            TypeError: If other is not an InterfaceABC instance.
            ValueError: If the interfaces have incompatible row or class properties.
        """
        if not isinstance(other, InterfaceABC):
            raise TypeError(f"Cannot concatenate Interface with {type(other)}")

        # Handle empty interfaces
        if len(self) == 0:
            return other
        if len(other) == 0:
            return self

        # Check compatibility - must have same row and class
        first_ep = next(iter(self))
        other_first_ep = next(iter(other))
        if first_ep.row != other_first_ep.row:
            raise ValueError(
                f"Cannot concatenate interfaces with different rows: {first_ep.row}"
                f" vs {other_first_ep.row}"
            )
        if first_ep.cls != other_first_ep.cls:
            raise ValueError(
                f"Cannot concatenate interfaces with different classes: {first_ep.cls}"
                f" vs {other_first_ep.cls}"
            )

        # For frozen interfaces, we need to create new tuples
        # Note: This returns a FrozenInterface, maintaining immutability
        new_type_tuple = self.type_tuple + tuple(ep.typ for ep in other)
        # Build refs_tuple - ep.refs is list[list[str | int]], convert to proper format
        other_refs = []
        for ep in other:
            ep_refs = tuple((ref[0], ref[1]) for ref in ep.refs)  # type: ignore
            other_refs.append(ep_refs)
        new_refs_tuple = self.refs_tuple + tuple(other_refs)

        return FrozenInterface(self.row, self.epcls, new_type_tuple, new_refs_tuple)

    def append(self, value: EndPointABC) -> None:
        """Append an endpoint to the interface.

        Args:
            value: The endpoint to append.

        Raises:
            RuntimeError: Always raises since frozen interfaces are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Interface")

    def extend(self, values: list[EndPointABC] | tuple[EndPointABC, ...] | InterfaceABC) -> None:
        """Extend the interface with multiple endpoints.

        Args:
            values: The endpoints to add.

        Raises:
            RuntimeError: Always raises since frozen interfaces are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Interface")

    def cls(self) -> EndPointClass:
        """Return the class of the interface.

        Returns:
            The EndPointClass (SRC or DST) of this interface.
        """
        return self.epcls

    def to_json(self, json_c_graph: bool = False) -> list:
        """Convert the interface to a JSON-compatible object.

        Args:
            json_c_graph: If True, returns a list suitable for JSON Connection Graph format.

        Returns:
            List of JSON-compatible endpoint representations.
        """
        return [ep.to_json(json_c_graph) for ep in self]

    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints).

        Returns:
            List of TypesDef UIDs for each endpoint.
        """
        return [typ.uid for typ in self.type_tuple]

    def types(self) -> tuple[list[int], bytes]:
        """Return a tuple of the ordered type UIDs and the indices into it.

        Returns:
            Tuple of (ordered_type_uids, byte_indices).
        """
        # Get unique types in sorted order
        unique_types = sorted(set(typ.uid for typ in self.type_tuple))

        # Create index mapping
        type_to_idx = {uid: idx for idx, uid in enumerate(unique_types)}

        # Create byte array of indices
        indices = bytes(type_to_idx[typ.uid] for typ in self.type_tuple)

        return unique_types, indices

    def ordered_td_uids(self) -> list[int]:
        """Return the ordered type definition UIDs.

        Returns:
            Sorted list of unique TypesDef UIDs.
        """
        return sorted(set(typ.uid for typ in self.type_tuple))

    def unconnected_eps(self) -> list[EndPointABC]:
        """Return a list of unconnected endpoints.

        Returns:
            List of FrozenEndPoint objects that have no connections.
        """
        return [ep for ep in self if not ep.is_connected()]

    def verify(self) -> None:
        """Verify the FrozenInterface object.

        Validates that the interface has valid structure and all endpoints are consistent.
        Empty interfaces are allowed as sentinel values.

        Raises:
            ValueError: If the interface is invalid.
            TypeError: If types are incorrect.
        """
        # Allow empty interfaces as sentinel values
        if len(self.type_tuple) == 0:
            return

        # Verify consistency of tuple lengths
        if len(self.type_tuple) != len(self.refs_tuple):
            raise ValueError(
                f"Type tuple length {len(self.type_tuple)} does not match "
                f"refs tuple length {len(self.refs_tuple)}"
            )

        # Verify all types are TypesDef instances
        for typ in self.type_tuple:
            if not isinstance(typ, TypesDef):
                raise TypeError(f"All types must be TypesDef instances, got {type(typ)}")

        # Verify all refs are properly structured
        for i, refs in enumerate(self.refs_tuple):
            if not isinstance(refs, tuple):
                raise TypeError(f"Endpoint {i} refs must be a tuple, got {type(refs)}")
            for j, ref in enumerate(refs):
                if not isinstance(ref, tuple):
                    raise TypeError(f"Endpoint {i} ref {j} must be a tuple, got {type(ref)}")
                if len(ref) != 2:
                    raise ValueError(
                        f"Endpoint {i} ref {j} must have exactly 2 elements, got {len(ref)}"
                    )
                if ref[0] not in ROW_SET:
                    raise ValueError(f"Endpoint {i} ref {j} has invalid row: {ref[0]}")
                if not isinstance(ref[1], int):
                    raise TypeError(f"Endpoint {i} ref {j} index must be int, got {type(ref[1])}")
                if not 0 <= ref[1] <= 255:
                    raise ValueError(f"Endpoint {i} ref {j} index must be 0-255, got {ref[1]}")

    def consistency(self) -> None:
        """Check the consistency of the FrozenInterface.

        Performs semantic validation that may be expensive. This method is called
        by verify() when CONSISTENCY logging is enabled.

        Validates:
            - All endpoints would pass their own consistency checks
            - Destination endpoints have at most 1 reference
            - Source endpoints reference destination rows
            - Destination endpoints reference source rows
        """
        # Verify endpoint consistency
        for idx in range(len(self.type_tuple)):
            refs = self.refs_tuple[idx]

            # Destination endpoints should have exactly 0 or 1 reference
            if self.epcls == EndPointClass.DST and len(refs) > 1:
                raise ValueError(
                    f"Destination endpoint {idx} can only have 0 or 1 reference, has {len(refs)}"
                )

            # Source endpoints reference destination rows, and vice versa
            if self.epcls == EndPointClass.SRC:
                for ref in refs:
                    if ref[0] not in DESTINATION_ROW_SET:
                        raise ValueError(
                            f"Source endpoint {idx} can only reference "
                            f"destination rows, got {ref[0]}"
                        )
            else:  # DST
                for ref in refs:
                    if ref[0] not in SOURCE_ROW_SET:
                        raise ValueError(
                            f"Destination endpoint {idx} can only reference"
                            f" source rows, got {ref[0]}"
                        )


class FrozenEndPoint(EndPointABC):
    """Frozen End Points are immutable and introspect FrozenInterface data structures directly.

    This class provides an immutable endpoint implementation that stores references as a
    tuple instead of a list. It is memory-efficient and suitable for frozen graphs.

    Attributes:
        row (Row): The row identifier where this endpoint resides.
        idx (int): The index of this endpoint within its row (stored externally,
                   accessed via context).
        cls (EndPointClass): The endpoint class - either SRC or DST (stored as epcls).
        typ (TypesDef): The data type associated with this endpoint.
        refs_tuple (tuple[tuple[Row, int], ...]): Immutable tuple of references
                   to connected endpoints.
    """

    __slots__ = ("typ", "refs_tuple", "row", "epcls", "idx", "cls", "refs", "_hash")

    def __init__(
        self,
        row: Row,
        idx: int,
        epcls: EndPointClass,
        typ: TypesDef,
        refs_tuple: tuple[tuple[Row, int], ...],
    ):
        super().__init__()
        self.row = row
        self.idx = idx
        self.epcls = epcls
        self.typ = typ
        self.refs_tuple = refs_tuple
        # Pre-compute hash for frozen endpoint
        self._hash = hash((self.row, self.idx, self.epcls, self.typ, self.refs_tuple))
        # Set cls and refs as attributes for ABC compatibility
        self.cls = epcls
        self.refs = [[ref[0], ref[1]] for ref in refs_tuple]

    def __eq__(self, value: object) -> bool:
        """Check equality of FrozenEndPoint instances.

        Two endpoints are equal if all their attributes match: row, idx, cls, typ,
        and refs (including the order and content of references).

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if all attributes are equal, False otherwise.
        """
        if not isinstance(value, EndPointABC):
            return False
        # Fast path for FrozenEndPoint comparison using hash
        if isinstance(value, FrozenEndPoint):
            return self._hash == value._hash
        # Slow path for comparison with mutable endpoints
        if len(self.refs_tuple) != len(value.refs):
            return False
        return (
            self.row == value.row
            and self.idx == value.idx
            and self.epcls == value.cls
            and self.typ == value.typ
            and all(
                (ref[0], ref[1]) == (vref[0], vref[1])
                for ref, vref in zip(self.refs_tuple, value.refs)
            )
        )

    def __ne__(self, value: object) -> bool:
        """Check inequality of FrozenEndPoint instances.

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if endpoints are not equal, False otherwise.
        """
        return not self.__eq__(value)

    def __hash__(self) -> int:
        """Return the hash of the endpoint.

        Returns pre-computed hash for O(1) performance.

        Returns:
            int: Hash value computed from all endpoint attributes.
        """
        return self._hash

    def __lt__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx < other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx < other.idx

    def __le__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx <= other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx <= other.idx

    def __gt__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx > other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx > other.idx

    def __ge__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx >= other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx >= other.idx

    def __str__(self) -> str:
        """Return the string representation of the endpoint.

        Provides a detailed string showing all endpoint attributes for debugging
        and logging purposes.

        Returns:
            str: String in format "FrozenEndPoint(row=X, idx=N, cls=CLS, typ=TYPE, refs=[...])"
        """
        return (
            f"FrozenEndPoint(row={self.row}, idx={self.idx}, cls={self.epcls}"
            f", typ={self.typ}, refs={list(self.refs_tuple)})"
        )

    def connect(self, other: EndPointABC) -> None:
        """Connect this endpoint to another endpoint.

        Args:
            other (EndPointABC): The endpoint to connect to.

        Raises:
            RuntimeError: Always raises since frozen endpoints are immutable.
        """
        raise RuntimeError("Cannot modify a frozen EndPoint")

    def is_connected(self) -> bool:
        """Check if the endpoint is connected.

        Determines whether this endpoint has any outgoing references to other endpoints.

        Returns:
            bool: True if the endpoint has at least one reference, False otherwise.
        """
        return len(self.refs_tuple) > 0

    def to_json(self, json_c_graph: bool = False) -> dict | list:
        """Convert the endpoint to a JSON-compatible object.

        Serializes the endpoint to a format suitable for JSON export. The format varies
        depending on the json_c_graph parameter.

        Args:
            json_c_graph (bool): If True, returns a list suitable for JSON Connection Graph format.
                                 Only valid for destination endpoints. Defaults to False.

        Returns:
            dict | list: JSON-compatible dictionary (standard format)
            or list (connection graph format).

        Raises:
            ValueError: If json_c_graph is True for a source endpoint or if
            endpoint is not connected.
        """
        if json_c_graph:
            # JSON Connection Graph format (destination endpoints only)
            if self.epcls == EndPointClass.SRC:
                raise ValueError(
                    "JSON Connection Graph format is only valid for destination endpoints"
                )
            if len(self.refs_tuple) != 1:
                raise ValueError(
                    f"Destination endpoint must have exactly 1 connection for JSON format, "
                    f"has {len(self.refs_tuple)}"
                )
            ref = self.refs_tuple[0]
            return [ref[0], ref[1], self.typ.name]
        else:
            # Standard format
            return {
                "row": self.row,
                "idx": self.idx,
                "cls": self.epcls.name,
                "typ": self.typ.name,
                "refs": [[ref[0], ref[1]] for ref in self.refs_tuple],
            }

    def verify(self) -> None:
        """Verify the FrozenEndPoint object.

        Validates that the endpoint has valid structure and types.

        Raises:
            ValueError: If the endpoint is invalid.
            TypeError: If types are incorrect.
        """
        # Validate row
        if self.row not in ROW_SET:
            raise ValueError(f"Invalid row: {self.row}")

        # Validate index
        if not isinstance(self.idx, int):
            raise TypeError(f"Index must be an integer, got {type(self.idx)}")
        if not 0 <= self.idx <= 255:
            raise ValueError(f"Index must be between 0 and 255, got {self.idx}")

        # Validate class
        if self.epcls not in (EndPointClass.SRC, EndPointClass.DST):
            raise ValueError(f"Invalid endpoint class: {self.epcls}")

        # Validate type
        if not isinstance(self.typ, TypesDef):
            raise TypeError(f"Type must be a TypesDef instance, got {type(self.typ)}")

        # Validate refs_tuple structure
        if not isinstance(self.refs_tuple, tuple):
            raise TypeError(f"refs_tuple must be a tuple, got {type(self.refs_tuple)}")

        for ref in self.refs_tuple:
            if not isinstance(ref, tuple):
                raise TypeError(f"Each reference must be a tuple, got {type(ref)}")
            if len(ref) != 2:
                raise ValueError(f"Each reference must have exactly 2 elements, got {len(ref)}")
            if ref[0] not in ROW_SET:
                raise ValueError(f"Invalid reference row: {ref[0]}")
            if not isinstance(ref[1], int):
                raise TypeError(f"Reference index must be an integer, got {type(ref[1])}")
            if not 0 <= ref[1] <= 255:
                raise ValueError(f"Reference index must be between 0 and 255, got {ref[1]}")

    def consistency(self) -> None:
        """Check the consistency of the FrozenEndPoint.

        Performs semantic validation that may be expensive. This method is called
        by verify() when CONSISTENCY logging is enabled.

        Validates:
            - Reference structure matches endpoint class rules
            - Source endpoints can have multiple refs, destinations only one
            - All references point to appropriate row types
        """
        # Destination endpoints should have exactly 0 or 1 reference
        if self.epcls == EndPointClass.DST and len(self.refs_tuple) > 1:
            raise ValueError(
                f"Destination endpoint can only have 0 or 1 reference, has {len(self.refs_tuple)}"
            )

        # Source endpoints reference destination rows, and vice versa
        if self.epcls == EndPointClass.SRC:
            for ref in self.refs_tuple:
                if ref[0] not in DESTINATION_ROW_SET:
                    raise ValueError(
                        f"Source endpoint can only reference destination rows, got {ref[0]}"
                    )
        else:  # DST
            for ref in self.refs_tuple:
                if ref[0] not in SOURCE_ROW_SET:
                    raise ValueError(
                        f"Destination endpoint can only reference source rows, got {ref[0]}"
                    )


class FrozenCGraph(CGraphABC, CommonObj):
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

    __slots__ = _UNDER_ROW_CLS_INDEXED + _UNDER_CON_CLS_INDEXED + ("_hash",)

    def __init__(self, graph: dict[str, list[EndpointMemberType]] | CGraphABC) -> None:
        """Initialize the Frozen Connection Graph.

        Args:
            graph: A dictionary mapping interface keys to Interface objects.

        Raises:
            TypeError: If graph is not a dict or contains invalid interface types.
            ValueError: If graph structure violates Connection Graph rules.
        """
        super().__init__()

        # Set type tuples and connection (reference) tuples for all interfaces
        # Interfaces are stored as
        #   tuple[TypesDef, ...]
        # References are stored as
        #   tuple[tuple[tuple[Row, idx], ...], ...]
        for key in ROW_CLS_INDEXED:
            _key = "_" + key
            if isinstance(graph, CGraphABC):
                type_tuple = tuple(ep.typ for ep in graph[key]) if key in graph else None
                con_tuple = (
                    tuple(
                        src_refs_store[tuple(refs_store[tuple(ref)] for ref in ep.refs)]
                        for ep in graph[key]
                    )
                    if key in graph
                    else None
                )
            else:
                type_tuple = tuple(ep[3] for ep in graph[key]) if key in graph else None
                con_tuple = (
                    tuple(
                        src_refs_store[tuple(refs_store[tuple(ref)] for ref in ep[4])]
                        for ep in graph[key]
                    )
                    if key in graph
                    else None
                )
            setattr(self, _key, type_tuple_store[type_tuple] if type_tuple is not None else None)
            setattr(self, _key + "c", refs_store[con_tuple] if con_tuple is not None else None)

        # Pre-compute the hash for the frozen graphs
        # For consistency, we use the same hash calculation as unfrozen graphs
        self._hash = hash(tuple(hash(iface) for iface in self.values()))

    # Container Protocol Methods (from Collection)

    def __contains__(self, key: object) -> bool:
        """Check if the interface exists in the Connection Graph.

        Args:
            key: Interface identifier, may be a row or row with class postfix.

        Returns:
            True if the interface exists, False otherwise.
        """
        assert isinstance(key, str), f"Key must be a string, got {type(key)}"
        if len(key) == 1:
            # Must be just a row - check both src and dst
            src_key = key + EPClsPostfix.SRC
            dst_key = key + EPClsPostfix.DST
            return (src_key in ROW_CLS_INDEXED and getattr(self, "_" + src_key) is not None) or (
                dst_key in ROW_CLS_INDEXED and getattr(self, "_" + dst_key) is not None
            )
        # Full key with class postfix
        if key not in ROW_CLS_INDEXED:
            return False
        return getattr(self, "_" + key) is not None

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the interface keys in the Connection Graph.

        Returns:
            Iterator over non-null interface keys.
        """
        return (key for key in ROW_CLS_INDEXED if getattr(self, "_" + key) is not None)

    def __len__(self) -> int:
        """Return the number of interfaces in the Connection Graph.

        Returns:
            Number of non-null interfaces.
        """
        return sum(1 for key in _UNDER_ROW_CLS_INDEXED if getattr(self, key) is not None)

    # Mapping Protocol Methods

    def __getitem__(self, key: str) -> InterfaceABC:
        """Get the interface with the given key.

        Args:
            key: Interface identifier e.g. 'Is', 'Bd' etc.

        Returns:
            The Interface object for the given key.

        Raises:
            KeyError: If the key is invalid.
        """
        assert isinstance(key, str), f"Key must be a string, got {type(key)}"
        if key not in ROW_CLS_INDEXED:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        _key = "_" + key
        typ_tuple = getattr(self, _key)
        if typ_tuple is None:
            raise KeyError(f"Connection Graph key not set: {key}")
        key_row = key[0]
        # key[1] is 's' or 'd' - compare directly
        is_src = key[1] == "s"
        epcls = EndPointClass.SRC if is_src else EndPointClass.DST
        row = SrcRow(key_row) if is_src else DstRow(key_row)
        return FrozenInterface(row, epcls, typ_tuple, getattr(self, _key + "c"))

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

    def get(self, key: str, default: InterfaceABC | None = None) -> InterfaceABC | None:
        """Get the interface with the given key, or return default if not found.

        Args:
            key: Interface identifier.
            default: Default value to return if key is not found.

        Returns:
            The Interface object for the given key, or default if not found.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> Iterator[str]:
        """Return an iterator over the interface keys in the Connection Graph.

        Returns:
            Iterator over non-null interface keys.
        """
        return iter(self)

    def values(self) -> Iterator[InterfaceABC]:
        """Return an iterator over the interfaces in the Connection Graph.

        Returns:
            Iterator over Interface objects.
        """
        for key in self:
            yield self[key]

    def items(self) -> Iterator[tuple[str, InterfaceABC]]:
        """Return an iterator over (key, interface) pairs in the Connection Graph.

        Returns:
            Iterator over (key, Interface) tuples.
        """
        for key in self:
            yield (key, self[key])

    # Comparison and Hashing Methods

    def __eq__(self, other: object) -> bool:
        """Check equality of Connection Graphs.

        Args:
            other: Object to compare with.

        Returns:
            True if graphs are equivalent, False otherwise.
        """
        if not isinstance(other, FrozenCGraph):
            return False
        return self._hash == other._hash

    def __hash__(self) -> int:
        """Return the hash of the Connection Graph.

        Returns:
            Pre-computed hash value for the frozen graph.
        """
        return self._hash

    # String Representation

    def __repr__(self) -> str:
        """Return a string representation of the Connection Graph.

        Returns:
            String representation suitable for debugging and logging.
        """
        return pformat(self.to_json(), indent=4, width=120)

    # Graph State Methods

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable.

        A stable graph has all destination endpoints connected to source endpoints.
        Frozen graphs are guaranteed to be stable.

        Returns:
            True (always, since frozen graphs are stable by definition).
        """
        return True

    def graph_type(self) -> CGraphType:
        """Identify and return the type of this connection graph.

        Returns:
            The CGraphType enum value representing this graph's type.
        """
        return c_graph_type(self)

    # Serialization Methods

    def to_json(self, json_c_graph: bool = False) -> dict | JSONCGraph:
        """Convert the Connection Graph to a JSON-compatible dictionary.

        Args:
            json_c_graph: If True, return a JSONCGraph format.

        Returns:
            JSON-compatible dictionary representation of the graph.
        """
        jcg: JSONCGraph = {}
        row_u = []
        # Process destination rows
        for dst_row in DstRow:
            dst_key = dst_row + EPClsPostfix.DST
            if dst_key in self:
                iface = self[dst_key]
                jcg[dst_row] = iface.to_json(json_c_graph=json_c_graph)

        # Process source rows to find unconnected endpoints
        for src_row in SrcRow:
            src_key = src_row + EPClsPostfix.SRC
            if src_key in self:
                iface = self[src_key]
                unconnected_srcs = [ep for ep in iface if not ep.is_connected()]
                row_u.extend([ep.row, ep.idx, ep.typ.name] for ep in unconnected_srcs)

        if row_u:
            jcg[DstRow.U] = row_u

        return jcg

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
        for key in ROW_CLS_INDEXED:
            if key in self:
                iface = self[key]
                iface.consistency()

        # Verify bidirectional reference consistency
        # Build separate maps for source and destination endpoints by (row, idx)
        src_ep_map: dict[tuple[str, int], FrozenEndPoint] = {}
        dst_ep_map: dict[tuple[str, int], FrozenEndPoint] = {}

        for key in ROW_CLS_INDEXED:
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
        for key in ROW_CLS_INDEXED:
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
        for key in ROW_CLS_INDEXED:
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

        for row in SINGLE_ONLY_ROWS:
            for cls_postfix in (EPClsPostfix.SRC, EPClsPostfix.DST):
                key = row + cls_postfix
                if key in self:
                    iface = self[key]
                    if len(iface) > 1:
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

    # FreezableObject Methods

    def freeze(self, store: bool = True) -> FrozenCGraph:
        """Freeze the graph.

        For FrozenCGraph, this is a no-op since the graph is always frozen.
        If store is True, the graph is stored in the object deduplicator for deduplication.

        Args:
            store: If True, store in the object deduplicator.

        Returns:
            Self (already frozen).
        """
        if store:
            # Use the global frozen_cgraph_store deduplicator
            return frozen_cgraph_store[self]
        return self

    def is_frozen(self) -> bool:
        """Check if the graph is frozen.

        Returns:
            True (always, since FrozenCGraph is always frozen).
        """
        return True


# Deduplication store for FrozenCGraph instances
frozen_cgraph_store: ObjectDeduplicator = ObjectDeduplicator("Frozen CGraph", 2**12)
