"""Endpoint class using builtin collections."""

from __future__ import annotations

from egpcommon.egp_log import VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    SINGLE_ONLY_ROWS,
    SOURCE_ROW_SET,
    DstRow,
    EndPointClass,
    Row,
    SrcRow,
)
from egppy.genetic_code.types_def import TypesDef, types_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class EndpointRef(FreezableObject):
    """Reference to an endpoint position (row and index).

    EndpointRef is a lightweight, immutable reference that identifies the position
    of an endpoint within an interface. It contains only the structural information
    (row and index) without type or connection information.
    """

    __slots__ = ("row", "idx", "_hash")

    def __init__(self, row: Row, idx: int, frozen: bool = False) -> None:
        """Initialize the endpoint reference.

        Args
        ----
        row: Row: The row this endpoint belongs to (e.g., DstRow.A, SrcRow.I)
        idx: int: The index of this endpoint in its interface (0-255)
        frozen: bool: If True, freeze the reference immediately after creation
        """
        super().__init__(False)
        self.row: Row = row
        self.idx: int = idx

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0
        if frozen:
            self.freeze()

    def __eq__(self, value: object) -> bool:
        """Check equality of EndpointRef instances."""
        if not isinstance(value, EndpointRef):
            return False
        return self.row == value.row and self.idx == value.idx

    def __hash__(self) -> int:
        """Return the hash of the endpoint reference."""
        if self.is_frozen():
            # Hash is defined in self.freeze() to ensure immutability
            return self._hash
        # Else it is dynamically defined.
        return hash((self.row, self.idx))

    def __ne__(self, value: object) -> bool:
        """Check inequality of EndpointRef instances."""
        return not self.__eq__(value)

    def __str__(self) -> str:
        """Return the string representation of the endpoint reference."""
        return f"EndpointRef(row={self.row}, idx={self.idx})"

    def __repr__(self) -> str:
        """Return the detailed representation of the endpoint reference."""
        return f"EndpointRef(row={self.row!r}, idx={self.idx!r})"

    def copy(self) -> EndpointRef:
        """Return a copy of the endpoint reference."""
        return EndpointRef(self.row, self.idx)

    def freeze(self, store: bool = True) -> EndpointRef:
        """Freeze the endpoint reference, making it immutable."""
        if not self.is_frozen():
            retval = super().freeze(store)
            # Need to jump through hoops to set the persistent hash
            object.__setattr__(self, "_hash", hash((self.row, self.idx)))

            # Some sanity checks
            if _logger.isEnabledFor(level=VERIFY):
                if not isinstance(self.idx, int) or not (0 <= self.idx < 256):
                    raise ValueError("Endpoint index must be an integer between 0 and 255.")
            return retval
        return self

    def to_json(self) -> dict:
        """Convert the endpoint reference to a JSON-compatible object."""
        return {
            "row": str(self.row),
            "idx": self.idx,
        }

    def to_tuple(self) -> tuple[str, int]:
        """Convert to a tuple representation."""
        return (str(self.row), self.idx)

    def to_list(self) -> list[str | int]:
        """Convert to a list representation."""
        return [str(self.row), self.idx]

    def verify(self) -> None:
        """Verify the integrity of the endpoint reference."""
        if self.idx < 0 or self.idx > 255:
            raise ValueError("Endpoint index must be between 0 and 255.")
        if self.row in SINGLE_ONLY_ROWS and self.idx != 0:
            raise ValueError(f"Row {self.row} can only have a single endpoint with index 0.")


# Specialized endpoint references for source and destination
class SrcEndpointRef(EndpointRef, name="EndpointRef"):
    """Source endpoint reference."""

    def __init__(self, row: SrcRow, idx: int, frozen: bool = False) -> None:
        """Initialize the source endpoint reference.

        Args
        ----
        row: SrcRow: The source row this endpoint belongs to
        idx: int: The index of this endpoint in its interface (0-255)
        frozen: bool: If True, freeze the reference immediately after creation
        """
        if isinstance(row, str):
            row = SrcRow(row)
        super().__init__(row, idx, frozen)

    def freeze(self, store: bool = True) -> SrcEndpointRef:
        """Freeze the source endpoint reference."""
        if not self.is_frozen():
            if _logger.isEnabledFor(level=VERIFY):
                if self.row not in SOURCE_ROW_SET:
                    raise ValueError(
                        f"Source endpoint row must be in SOURCE_ROW_SET, got {self.row}"
                    )
            super().freeze(store)
        return self

    def verify(self) -> None:
        """Verify the integrity of the source endpoint reference."""
        super().verify()
        if self.row not in SOURCE_ROW_SET:
            raise ValueError(f"Source endpoint row must be in SOURCE_ROW_SET, got {self.row}")


class DstEndpointRef(EndpointRef, name="EndpointRef"):
    """Destination endpoint reference."""

    def __init__(self, row: DstRow, idx: int, frozen: bool = False) -> None:
        """Initialize the destination endpoint reference.

        Args
        ----
        row: DstRow: The destination row this endpoint belongs to
        idx: int: The index of this endpoint in its interface (0-255)
        frozen: bool: If True, freeze the reference immediately after creation
        """
        if isinstance(row, str):
            row = DstRow(row)
        super().__init__(row, idx, frozen)

    def freeze(self, store: bool = True) -> DstEndpointRef:
        """Freeze the destination endpoint reference."""
        if not self.is_frozen():
            if _logger.isEnabledFor(level=VERIFY):
                if self.row not in DESTINATION_ROW_SET:
                    raise ValueError(
                        f"Destination endpoint row must be in DESTINATION_ROW_SET, got {self.row}"
                    )
            super().freeze(store)
        return self

    def verify(self) -> None:
        """Verify the integrity of the destination endpoint reference."""
        super().verify()
        if self.row not in DESTINATION_ROW_SET:
            raise ValueError(
                f"Destination endpoint row must be in DESTINATION_ROW_SET, got {self.row}"
            )


class EndPoint(FreezableObject):
    """Endpoint class representing endpoint identity without connections.

    An endpoint represents a typed parameter position in an interface.
    Connections to/from this endpoint are managed separately by Interface.
    This allows endpoints with the same identity to be deduplicated regardless
    of their connections.
    """

    __slots__ = ("ref", "cls", "_typ", "_hash")

    def __init__(
        self,
        row: Row,
        idx: int,
        cls: EndPointClass,
        typ: TypesDef | int | str,
        frozen: bool = False,
    ) -> None:
        """Initialize the endpoint.

        Args
        ----
        row: Row: The row this endpoint belongs to (e.g., DstRow.A, SrcRow.I)
        idx: int: The index of this endpoint in its interface (0-255)
        cls: EndPointClass: Whether this is a source or destination endpoint
        typ: TypesDef | int | str: The EGP type of this endpoint
        frozen: bool: If True, freeze the endpoint immediately after creation
        """
        super().__init__(False)
        # Create appropriate EndpointRef based on class
        if cls == EndPointClass.SRC:
            self.ref: EndpointRef = SrcEndpointRef(
                SrcRow(row) if isinstance(row, str) else row, idx
            )
        else:
            self.ref = DstEndpointRef(DstRow(row) if isinstance(row, str) else row, idx)
        self.cls = cls
        self.typ = typ

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0
        if frozen:
            self.freeze()

    @property
    def row(self) -> Row:
        """Return the row of the endpoint."""
        return self.ref.row

    @property
    def idx(self) -> int:
        """Return the index of the endpoint."""
        return self.ref.idx

    @property
    def typ(self) -> TypesDef:
        """Return the type of the endpoint."""
        return self._typ

    @typ.setter
    def typ(self, typ: TypesDef | int | str) -> None:
        """Validate and set the type."""
        if self._frozen:
            raise RuntimeError("Cannot set type on a frozen EndPoint")
        assert isinstance(typ, (TypesDef, int, str)), f"Invalid type: {typ}"
        self._typ: TypesDef = types_def_store[typ] if isinstance(typ, (int, str)) else typ

    def __eq__(self, value: object) -> bool:
        """Check equality of EndPoint instances based on identity only."""
        if not isinstance(value, EndPoint):
            return False
        return self.ref == value.ref and self.cls == value.cls and self.typ == value.typ

    def __ge__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPoint):
            return NotImplemented
        return self.idx >= other.idx

    def __gt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPoint):
            return NotImplemented
        return self.idx > other.idx

    def __hash__(self) -> int:
        """Return the hash of the endpoint based on identity only."""
        if self.is_frozen():
            # Hash is defined in self.freeze() to ensure immutability
            return self._hash
        # Else it is dynamically defined.
        return hash((self.ref, self.cls, self.typ))

    def __le__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPoint):
            return NotImplemented
        return self.idx <= other.idx

    def __lt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on thier idx"""
        if not isinstance(other, EndPoint):
            return NotImplemented
        return self.idx < other.idx

    def __ne__(self, value: object) -> bool:
        """Check inequality of EndPoint instances."""
        return not self.__eq__(value)

    def __str__(self) -> str:
        """Return the string representation of the endpoint."""
        return f"EndPoint(row={self.row}, idx={self.idx}, cls={self.cls}" f", typ={self.typ})"

    def copy(self, new_idx: int | None = None) -> EndPoint:
        """Return a copy of the endpoint.

        Args
        ----
        new_idx: int | None: If provided, create the copy with a different index.
                             Otherwise, use the same index as the original.
        """
        idx = new_idx if new_idx is not None else self.ref.idx
        return EndPoint(
            self.ref.row,
            idx,
            self.cls,
            self.typ,
        )

    def freeze(self, store: bool = True) -> EndPoint:
        """Freeze the endpoint, making it immutable."""
        if not self.is_frozen():
            # Freeze the ref first
            self.ref.freeze(store)
            retval = super().freeze(store)
            # Need to jump through hoops to set the persistent hash
            object.__setattr__(self, "_hash", hash((self.ref, self.cls, self.typ)))

            # Some sanity checks
            if _logger.isEnabledFor(level=VERIFY):
                if not (
                    (self.ref.row in DESTINATION_ROW_SET and self.cls == EndPointClass.DST)
                    or (self.ref.row in SOURCE_ROW_SET and self.cls == EndPointClass.SRC)
                ):
                    raise ValueError("Endpoint row is not consistent with the endpoint class.")
                if not isinstance(self.typ, TypesDef):
                    raise TypeError("Endpoint type must be a TypesDef instance.")
            return retval
        return self

    def to_json(self) -> dict:
        """Convert the endpoint to a JSON-compatible object.

        Returns a dictionary representation. Note: connections are NOT included
        as they are managed separately by Interface.
        """
        return {
            "row": str(self.ref.row),
            "idx": self.ref.idx,
            "cls": self.cls,
            "typ": str(self.typ),
        }

    def verify(self) -> None:
        """Verify the integrity of the endpoint."""
        # Verify the ref
        self.ref.verify()

        # Check consistency between ref and cls
        if self.ref.row not in DESTINATION_ROW_SET and self.cls == EndPointClass.DST:
            raise ValueError("Destination endpoint row must be a destination row.")
        if self.ref.row not in SOURCE_ROW_SET and self.cls == EndPointClass.SRC:
            raise ValueError("Source endpoint row must be a source row.")


# Re-use the EndPoint object deduplicator for both SrcEndPoint and DstEndPoint
class SrcEndPoint(EndPoint, name="Endpoint"):
    """Source EndPoint class."""

    def __init__(
        self,
        row: SrcRow,
        idx: int,
        typ: TypesDef | int | str,
        frozen: bool = False,
    ) -> None:
        """Initialize the source endpoint."""
        super().__init__(row, idx, EndPointClass.SRC, typ, frozen)


class DstEndPoint(EndPoint, name="Endpoint"):
    """Destination EndPoint class."""

    def __init__(
        self,
        row: DstRow,
        idx: int,
        typ: TypesDef | int | str,
        frozen: bool = False,
    ) -> None:
        """Initialize the destination endpoint."""
        super().__init__(row, idx, EndPointClass.DST, typ, frozen)
