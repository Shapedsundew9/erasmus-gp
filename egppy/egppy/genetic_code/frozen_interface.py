"""Immutable interface implementation for FrozenCGraph data structures."""

from typing import Iterator

from egpcommon.deduplication import refs_store
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SOURCE_ROW_SET,
    EPCls,
    Row,
    SrcRow,
)
from egppy.genetic_code.endpoint_abc import FrozenEndPointABC
from egppy.genetic_code.ep_ref_abc import FrozenEPRefABC, FrozenEPRefsABC
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.frozen_ep_ref import FrozenEPRef, FrozenEPRefs
from egppy.genetic_code.interface_abc import FrozenInterfaceABC
from egppy.genetic_code.types_def import TypesDef


class FrozenInterface(FrozenInterfaceABC):
    """Frozen interfaces are immutable and introspect FrozenCGraph data structures directly.

    This class provides an immutable interface implementation that stores endpoint data
    as tuples instead of lists. It creates FrozenEndPoint instances on-the-fly when accessed.

    Attributes:
        row: Row: The row of the interface. The correct row enum must be used (DstRow or SrcRow).
        type_tuple (tuple[TypesDef, ...]): Tuple of types for each endpoint.
        refs_tuple (tuple[FrozenEPRefs, ...]): Tuple of reference tuples for each endpoint.
    """

    __slots__ = ("_row", "_cls", "type_tuple", "refs_tuple", "_hash")

    def __init__(
        self,
        row: Row,
        type_tuple: tuple[TypesDef, ...],
        refs_tuple: tuple[tuple[tuple[Row, int], ...], ...] | tuple[FrozenEPRefs, ...],
    ):
        super().__init__()
        self._row = row
        self._cls = EPCls.SRC if isinstance(row, SrcRow) else EPCls.DST
        self.type_tuple = type_tuple
        # Convert refs_tuple to tuple of FrozenEPRefs
        refs_list = []
        for refs in refs_tuple:
            # pylint: disable=unidiomatic-typecheck
            # (cannot be an EPRefs)
            if type(refs) is FrozenEPRefs:
                refs_list.append(refs)
            else:
                # refs is tuple of (row, idx) tuples
                refs_list.append(refs_store[FrozenEPRefs(FrozenEPRef(r[0], r[1]) for r in refs)])
        self.refs_tuple = tuple(refs_list)
        # Pre-compute hash for frozen interface
        self._hash = hash((self._row, self._cls, self.type_tuple, self.refs_tuple))

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
        """Check equality of FrozenInterface instances.

        Args:
            value: Object to compare with.

        Returns:
            True if equal, False otherwise.
        """
        if not isinstance(value, FrozenInterfaceABC):
            return False
        # Fast path for FrozenInterface comparison
        if isinstance(value, FrozenInterface):
            return self._hash == value._hash
        # Slow path for comparison with mutable interfaces
        if len(self) != len(value):
            return False
        return all(a == b for a, b in zip(self, value))

    def __getitem__(self, idx: int) -> FrozenEndPointABC:
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
            self._row,
            idx,
            self._cls,
            self.type_tuple[idx],
            self.refs_tuple[idx],
        )

    def __hash__(self) -> int:
        """Return the hash of the interface.

        Returns:
            Pre-computed hash value for the frozen interface.
        """
        return self._hash

    def __iter__(self) -> Iterator[FrozenEndPointABC]:
        """Return an iterator over the endpoints.

        Returns:
            Iterator over FrozenEndPoint objects in the interface.
        """
        for idx, typ in enumerate(self.type_tuple):
            yield FrozenEndPoint(
                self._row,
                idx,
                self._cls,
                typ,
                self.refs_tuple[idx],
            )

    def __len__(self) -> int:
        """Return the number of endpoints in the interface.

        Returns:
            Number of endpoints in this interface.
        """
        return len(self.type_tuple)

    def __str__(self) -> str:
        """Return the string representation of the interface.

        Returns:
            String representation of the interface.
        """
        return f"FrozenInterface({', '.join(str(typ) for typ in self.type_tuple)})"

    def consistency(self) -> None:
        """Check the consistency of the FrozenInterface.

        Performs semantic validation that may be expensive. This method is called
        by verify() when CONSISTENCY integrity is enabled.

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
            if self._cls == EPCls.DST and len(refs) > 1:
                raise ValueError(
                    f"Destination endpoint {idx} can only have 0 or 1 reference, has {len(refs)}"
                )

            # Source endpoints reference destination rows, and vice versa
            if self._cls == EPCls.SRC:
                for ref in refs:
                    if ref.row not in DESTINATION_ROW_SET:
                        raise ValueError(
                            f"Source endpoint {idx} can only reference "
                            f"destination rows, got {ref.row}"
                        )
            else:  # DST
                for ref in refs:
                    if ref.row not in SOURCE_ROW_SET:
                        raise ValueError(
                            f"Destination endpoint {idx} can only reference"
                            f" source rows, got {ref.row}"
                        )

    def ept_type_match(self, other: FrozenInterfaceABC) -> bool:
        """Check if the endpoint types match another interface.

        The type, order and number of endpoints must be identical for match to be true.

        Args:
            other: The other interface to compare with.
        Returns:
            True if endpoint types match, False otherwise.
        """
        if len(self) != len(other):
            return False
        for ep_self, ep_other in zip(self.type_tuple, other):
            if ep_self != ep_other.typ:
                return False
        return True

    def sorted_unique_td_uids(self) -> list[int]:
        """Return the ordered type definition UIDs.

        Returns:
            Sorted list of unique TypesDef UIDs.
        """
        return sorted(set(typ.uid for typ in self.type_tuple))

    def to_json(self, json_c_graph: bool = False) -> list:
        """Convert the interface to a JSON-compatible object.

        Args:
            json_c_graph: If True, returns a list suitable for JSON Connection Graph format.

        Returns:
            List of JSON-compatible endpoint representations.
        """
        return [ep.to_json(json_c_graph) for ep in self]

    def to_td(self) -> tuple[TypesDef, ...]:
        """Convert the interface to a tuple of TypesDef objects.

        Returns:
            Tuple of TypesDef objects for each endpoint.
        """
        return self.type_tuple

    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints).

        Returns:
            List of TypesDef UIDs for each endpoint.
        """
        return [typ.uid for typ in self.type_tuple]

    def types_and_indices(self) -> tuple[list[int], bytes]:
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

    def unconnected_eps(self) -> list[FrozenEndPointABC]:
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
            if not isinstance(refs, FrozenEPRefsABC):
                raise TypeError(f"Endpoint {i} refs must be FrozenEPRefsABC, got {type(refs)}")
            for j, ref in enumerate(refs):
                if not isinstance(ref, FrozenEPRefABC):
                    raise TypeError(f"Endpoint {i} ref {j} must be FrozenEPRefABC, got {type(ref)}")
                if ref.row not in ROW_SET:
                    raise ValueError(f"Endpoint {i} ref {j} has invalid row: {ref.row}")
                if not isinstance(ref.idx, int):
                    raise TypeError(f"Endpoint {i} ref {j} index must be int, got {type(ref.idx)}")
                if not 0 <= ref.idx <= 255:
                    raise ValueError(f"Endpoint {i} ref {j} index must be 0-255, got {ref.idx}")
