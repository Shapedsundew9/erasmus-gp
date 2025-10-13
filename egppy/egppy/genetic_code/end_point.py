"""Endpoint class using builtin collections."""

from __future__ import annotations

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egpcommon.object_set import ObjectSet
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
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
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Create object sets for references and tuples of references
ref_store = ObjectSet("Endpoint reference store")
ref_tuple_store = ObjectSet("Endpoint reference tuple store")


class EndPoint(FreezableObject):
    """Endpoint class using builtin collections."""

    __slots__ = ("row", "idx", "cls", "_typ", "_refs", "_hash")

    def __init__(
        self,
        row: Row,
        idx: int,
        cls: EndPointClass,
        typ: TypesDef | int | str,
        refs: list[str] | list[list[str | int]] | tuple[tuple[str, int], ...] | None = None,
        frozen: bool = False,
    ) -> None:
        """Initialize the endpoint."""
        super().__init__(False)
        self.row = row
        self.idx = idx
        self.cls = cls
        self.typ = typ
        self.refs = refs if refs is not None else []

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0
        if frozen:
            self.freeze()

    @property
    def refs(self) -> list[list[str | int]] | tuple[tuple[str, int], ...]:
        """Return the references of the endpoint."""
        return self._refs

    @refs.setter
    def refs(self, refs: list[str] | list[list[str | int]] | tuple[tuple[str, int], ...]) -> None:
        """Validate and set the references. This will always return a list of lists."""
        if self._frozen:
            raise RuntimeError("Cannot set references on a frozen EndPoint")
        assert isinstance(refs, (list, tuple)), f"Invalid references: {refs}"
        self._refs = []
        for ref in refs:
            if isinstance(ref, str):
                if _logger.isEnabledFor(level=DEBUG):
                    if not len(ref) == 4:
                        raise ValueError(f"Invalid reference string length: {len(ref)} != 4")
                    if not ref[0] in ROW_SET:
                        raise ValueError(f"Invalid reference row: {ref[0]}")
                    if not 0 <= int(ref[1:]) < 256:
                        raise ValueError(f"Invalid reference index: {ref[1:]}")
                    if ref[0] in SINGLE_ONLY_ROWS and int(ref[1:]) != 0:
                        raise ValueError(f"Row {ref[0]} can only have single connections.")
                r: str = ref[0]
                i = int(ref[1:])
            elif isinstance(ref, (list, tuple)):
                if _logger.isEnabledFor(level=DEBUG):
                    if not len(ref) == 2:
                        raise ValueError(f"Invalid reference sequence length: {len(ref)} != 2")
                    if not ref[0] in ROW_SET:
                        raise ValueError(f"Invalid reference row: {ref[0]}")
                    if not (isinstance(ref[1], int) and 0 <= ref[1] < 256):
                        raise ValueError(f"Invalid reference index: {ref[1]}")
                    if ref[0] in SINGLE_ONLY_ROWS and ref[1] != 0:
                        raise ValueError(f"Row {ref[0]} can only have single connections.")
                assert isinstance(ref[0], str), f"Invalid reference row type: {type(ref[0])}"
                assert isinstance(ref[1], int), f"Invalid reference index type: {type(ref[1])}"
                r: str = ref[0]
                i: int = ref[1]
            else:
                raise TypeError(f"Invalid reference type: {type(ref)}")
            self._refs.append([r, i])

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
        """Check equality of EndPoint instances."""
        if not isinstance(value, EndPoint):
            return False
        return (
            self.row == value.row
            and self.idx == value.idx
            and self.cls == value.cls
            and self.typ == value.typ
            and self.refs == value.refs
        )

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
        """Return the hash of the endpoint."""
        if self.is_frozen():
            # Hash is defined in self.freeze() to ensure immutability
            return self._hash
        # Else it is dynamically defined.
        tuple_refs = tuple(tuple(ref) for ref in self.refs)
        return hash((self.row, self.idx, self.cls, self.typ, tuple_refs))

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
        return (
            f"EndPoint(row={self.row}, idx={self.idx}, cls={self.cls}"
            f", typ={self.typ}, refs=[{self.refs}])"
        )

    def connect(self, other: EndPoint) -> None:
        """Connect this endpoint to another endpoint."""
        if _logger.isEnabledFor(level=DEBUG):
            if self._frozen:
                raise RuntimeError("Cannot modify a frozen EndPoint")
            if not isinstance(other, EndPoint):
                raise TypeError(f"Expected EndPoint, got {type(other)}")
            if other.is_frozen():
                raise RuntimeError("Cannot connect to a frozen EndPoint")
            if self.cls == EndPointClass.DST and len(self.refs) > 1:
                raise ValueError("Destination endpoints can only have one reference.")
        if self.cls == EndPointClass.DST:
            self.refs = [[other.row, other.idx]]
        else:
            assert isinstance(self.refs, list), "References must be a list for source endpoints."
            self.refs.append([other.row, other.idx])

    def copy(self, clean: bool = False) -> EndPoint:
        """Return a copy of the endpoint with no references."""
        return EndPoint(
            self.row,
            self.idx,
            self.cls,
            self.typ,
            [] if clean else [list(ref) for ref in self.refs],
        )

    def freeze(self, store: bool = True) -> EndPoint:
        """Freeze the endpoint, making it immutable."""
        if not self.is_frozen():
            # Need to make references immutable
            object.__setattr__(self, "_refs", tuple(tuple(ref) for ref in self.refs))
            retval = super().freeze(store)
            # Need to jump through hoops to set the persistent hash
            object.__setattr__(
                self, "_hash", hash((self.row, self.idx, self.cls, self.typ, self.refs))
            )

            # Some sanity checks
            if _logger.isEnabledFor(level=VERIFY):
                if not (
                    (self.row in DESTINATION_ROW_SET and self.cls == EndPointClass.DST)
                    or (self.row in SOURCE_ROW_SET and self.cls == EndPointClass.SRC)
                ):
                    raise ValueError("Endpoint row is not consistent with the endpoint class.")
                if not (isinstance(self.idx, int) and 0 <= self.idx < 256):
                    raise ValueError("Endpoint index must be an integer between 0 and 255.")
                if not isinstance(self.typ, TypesDef):
                    raise TypeError("Endpoint type must be a TypesDef instance.")
                if not (
                    (len(self.refs) == 1 and self.cls == EndPointClass.DST)
                    or self.cls == EndPointClass.SRC
                ):
                    raise ValueError(
                        "Endpoint must have exactly one reference if it is a destination."
                    )
                if not (
                    (
                        all(ref[0] in SOURCE_ROW_SET for ref in self.refs)
                        and self.cls == EndPointClass.DST
                    )
                    or self.cls == EndPointClass.SRC
                ):
                    raise ValueError(
                        "All destination endpoint references must be a valid source row."
                    )
                if not (
                    (
                        all(ref[0] in DESTINATION_ROW_SET for ref in self.refs)
                        and self.cls == EndPointClass.SRC
                    )
                    or self.cls == EndPointClass.DST
                ):
                    raise ValueError(
                        "All source endpoint references must be a valid destination row."
                    )
                if not all(0 <= ref[1] < 256 for ref in self.refs if isinstance(ref[1], int)):
                    raise ValueError("All reference indices must be between 0 and 255.")
            return retval
        return self

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

    def verify(self) -> bool:
        """Verify the integrity of the endpoint."""
        if self.idx < 0 or self.idx > 255:
            raise ValueError("Endpoint index must be between 0 and 255.")
        if self.row in SINGLE_ONLY_ROWS and self.idx != 0:
            raise ValueError(f"Row {self.row} can only have a single endpoint with index 0.")
        if self.row not in DESTINATION_ROW_SET and self.cls == EndPointClass.DST:
            raise ValueError("Destination endpoint row must be a destination row.")
        if self.row not in SOURCE_ROW_SET and self.cls == EndPointClass.SRC:
            raise ValueError("Source endpoint row must be a source row.")
        if self.row in SINGLE_ONLY_ROWS and len(self.refs) > 1:
            raise ValueError(f"Row {self.row} can only have a single reference.")
        return True


class SourceEndPoint(EndPoint):
    """Source EndPoint class."""

    def __init__(
        self,
        row: SrcRow,
        idx: int,
        typ: TypesDef | int | str,
        refs: list[str] | list[list[str | int]] | tuple[tuple[str, int], ...] | None = None,
        frozen: bool = False,
    ) -> None:
        """Initialize the source endpoint."""
        super().__init__(row, idx, EndPointClass.SRC, typ, refs, frozen)


class DestinationEndPoint(EndPoint):
    """Destination EndPoint class."""

    def __init__(
        self,
        row: DstRow,
        idx: int,
        typ: TypesDef | int | str,
        refs: list[str] | list[list[str | int]] | tuple[tuple[str, int], ...] | None = None,
        frozen: bool = False,
    ) -> None:
        """Initialize the destination endpoint."""
        super().__init__(row, idx, EndPointClass.DST, typ, refs, frozen)
