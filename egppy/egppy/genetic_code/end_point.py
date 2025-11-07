"""Endpoint class using builtin collections."""

from __future__ import annotations

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.object_deduplicator import ObjectDeduplicator
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    SINGLE_ONLY_ROWS,
    SOURCE_ROW_SET,
    EndPointClass,
    Row,
)
from egppy.genetic_code.end_point_abc import EndPointABC
from egppy.genetic_code.types_def import TypesDef, types_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Create object sets for references and tuples of references
ref_store = ObjectDeduplicator("Endpoint reference store", 2**12)
ref_tuple_store = ObjectDeduplicator("Endpoint reference tuple store", 2**12)


class EndPoint(CommonObj, EndPointABC):
    """Endpoint class using builtin collections.

    This concrete implementation of EndPointABC uses builtin collections for
    efficient storage and manipulation of endpoint data. It supports both mutable
    and immutable (frozen) states with object deduplication for memory efficiency.
    """

    __slots__ = ("row", "idx", "cls", "typ", "refs")

    def __init__(self, *args) -> None:
        """Initialize the endpoint."""
        super().__init__()
        if len(args) == 1:
            if isinstance(args[0], EndPointABC):
                other: EndPointABC = args[0]
                self.row = other.row
                self.idx = other.idx
                self.cls = other.cls
                self.typ = other.typ
                self.refs = [list(ref) for ref in other.refs]
            elif isinstance(args[0], tuple) and len(args[0]) == 5:
                self.row, self.idx, self.cls, self.typ, refs_arg = args[0]
                self.refs = [] if refs_arg is None else [list(ref) for ref in refs_arg]
            else:
                raise TypeError("Invalid argument for EndPoint constructor")
        elif len(args) == 4 or len(args) == 5:
            self.row: Row = args[0]
            self.idx: int = args[1]
            self.cls: EndPointClass = args[2]
            self.typ = args[3] if isinstance(args[3], TypesDef) else types_def_store[args[3]]
            refs_arg = args[4] if len(args) == 5 and args[4] is not None else []
            self.refs = [list(ref) for ref in refs_arg]
        else:
            raise TypeError("Invalid arguments for EndPoint constructor")

    def __eq__(self, value: object) -> bool:
        """Check equality of EndPoint instances."""
        if not isinstance(value, EndPointABC):
            return False
        return hash(self) == hash(value)

    def __ge__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx >= other.idx

    def __gt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx > other.idx

    def __hash__(self) -> int:
        """Return the hash of the endpoint."""
        tuple_refs = tuple(tuple(ref) for ref in self.refs)
        return hash((self.row, self.idx, self.cls, self.typ, tuple_refs))

    def __le__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx <= other.idx

    def __lt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting. Endpoints are compared on their idx."""
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx < other.idx

    def __ne__(self, value: object) -> bool:
        """Check inequality of EndPoint instances."""
        return not self.__eq__(value)

    def __str__(self) -> str:
        """Return the string representation of the endpoint."""
        return (
            f"EndPoint(row={self.row}, idx={self.idx}, cls={self.cls}"
            f", typ={self.typ}, refs=[{self.refs}])"
        )

    def connect(self, other: EndPointABC) -> None:
        """Connect this endpoint to another endpoint."""
        if self.cls == EndPointClass.DST:
            self.refs = [[other.row, other.idx]]
        else:
            self.refs.append([other.row, other.idx])

    def is_connected(self) -> bool:
        """Check if the endpoint is connected."""
        return len(self.refs) > 0

    def to_json(self, json_c_graph: bool = False) -> dict | list:
        """Convert the endpoint to a JSON-compatible object.

        If `json_c_graph` is True, it returns a list suitable for JSON Connection Graph format.
        """
        if json_c_graph and self.cls == EndPointClass.DST:
            return [self.refs[0][0], self.refs[0][1], str(self.typ)]
        if json_c_graph and self.cls == EndPointClass.SRC:
            raise ValueError(
                "Source endpoints cannot be converted to JSON Connection Graph format."
            )
        return {
            "row": str(self.row),
            "idx": self.idx,
            "cls": self.cls,
            "typ": str(self.typ),
            "refs": [list(ref) for ref in self.refs],
        }

    def verify(self) -> None:
        """Verify the integrity of the endpoint."""
        self.value_error(0 <= self.idx < 256, "Endpoint index must be between 0 and 255.")
        self.value_error(
            (self.row in DESTINATION_ROW_SET and self.cls == EndPointClass.DST)
            or (self.cls == EndPointClass.SRC),
            "Destination endpoint row must be a destination row.",
        )
        self.value_error(
            (self.row in SOURCE_ROW_SET and self.cls == EndPointClass.SRC)
            or (self.cls == EndPointClass.DST),
            "Source endpoint row must be a source row.",
        )
        self.value_error(
            (self.row in SINGLE_ONLY_ROWS and self.idx == 0) or (self.row not in SINGLE_ONLY_ROWS),
            f"Row {self.row} can only have a single reference.",
        )
        self.value_error(
            (self.cls == EndPointClass.DST and len(self.refs) <= 1)
            or (self.cls == EndPointClass.SRC),
            "Destination endpoints cannot have more than one reference.",
        )


class SrcEndPoint(EndPoint):
    """Source Endpoint class."""

    def __init__(self, *args) -> None:
        """Initialize the source endpoint."""
        super().__init__(
            args[0], args[1], EndPointClass.SRC, args[2], args[3] if len(args) == 4 else None
        )


class DstEndPoint(EndPoint):
    """Destination Endpoint class."""

    def __init__(self, *args) -> None:
        """Initialize the destination endpoint."""
        super().__init__(
            args[0], args[1], EndPointClass.DST, args[2], args[3] if len(args) == 4 else None
        )
