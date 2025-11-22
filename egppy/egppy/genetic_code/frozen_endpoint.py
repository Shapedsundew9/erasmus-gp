"""Frozen Endpoint implementation for immutable graphs."""

from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SOURCE_ROW_SET,
    EndPointClass,
    Row,
)
from egppy.genetic_code.endpoint_abc import EndPointABC
from egppy.genetic_code.types_def import TypesDef


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
            return [str(ref[0]), ref[1], self.typ.name]
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

    def clr_refs(self) -> EndPointABC:
        """Clear all references in the endpoint."""
        raise RuntimeError("Cannot modify a frozen EndPoint")

    def ref_shift(self, shift: int) -> EndPointABC:
        """Shift all references in the endpoint by a given amount.

        Args:
            shift (int): The amount to shift each reference index.
        Raises:
            RuntimeError: Always raises since frozen endpoints are immutable.
        """
        raise RuntimeError("Cannot modify a frozen EndPoint")

    def set_ref(self, row: Row, idx: int, append: bool = False) -> EndPointABC:
        """Set or append to the references for an endpoint.

        This method always sets (replaces) the reference of a destination endpoint
        to the specified row and index. For a source endpoint, it appends the new reference
        to the existing list of references if append is True; otherwise, it replaces the
        entire list with the new reference.

        Args:
            row (Row): The row of the endpoint to reference.
            idx (int): The index of the endpoint to reference.
            append (bool): If True and the endpoint is a source, append the new reference;
                           otherwise, replace the references. Defaults to False.
        Returns:
            EndPointABC: Self with the reference set.
        """
        raise RuntimeError("Cannot modify a frozen EndPoint")
