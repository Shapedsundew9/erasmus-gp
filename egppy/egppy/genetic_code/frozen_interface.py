"""Immutable interface implementation for FrozenCGraph data structures."""

from typing import Iterator

from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SOURCE_ROW_SET,
    EndPointClass,
    Row,
)
from egppy.genetic_code.endpoint_abc import EndPointABC
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.interface_abc import InterfaceABC
from egppy.genetic_code.types_def import TypesDef


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

    def set_cls(self, ep_cls) -> InterfaceABC:
        """Set the class of all endpoints in the interface.

        Args:
            ep_cls: The EndPointClass to set (SRC or DST).

        Raises:
            RuntimeError: Always raises since frozen interfaces are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Interface")

    def set_row(self, row) -> InterfaceABC:
        """Set the row of all endpoints in the interface.

        Args:
            row: The Row to set.

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

    def clr_refs(self) -> InterfaceABC:
        """Clear all references in the interface endpoints."""
        raise RuntimeError("Cannot modify a frozen Interface")

    def ref_shift(self, shift: int) -> InterfaceABC:
        """Shift all reference indices in the interface endpoints.

        Args:
            shift: The integer amount to shift all reference indices by.
        Raises:
            RuntimeError: Always raises since frozen interfaces are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Interface")

    def set_refs(self, row: Row, start_ref: int = 0) -> InterfaceABC:
        """Set references for all endpoints in the interface.

        Args:
            row: The Row to set (e.g., IS, OD).
            start_ref: The starting reference number.

        Raises:
            RuntimeError: Always raises since frozen interfaces are immutable.
        """
        raise RuntimeError("Cannot modify a frozen Interface")
