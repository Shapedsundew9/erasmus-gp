"""Endpoint class using builtin collections."""

from __future__ import annotations

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egpcommon.object_set import ObjectSet
from egpcommon.properties import CGraphType
from egppy.c_graph.end_point.types_def.types_def import TypesDef, types_def_store
from egppy.c_graph.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROWS,
    SOURCE_ROW_SET,
    Row,
    EndPointClass,
)
from egppy.c_graph.c_graph_validation import CGT_VALID_DST_ROWS, CGT_VALID_SRC_ROWS


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

    __slots__ = ("_row", "_idx", "_cls", "_typ", "_refs", "_hash")

    def __init__(
        self,
        row: Row,
        idx: int,
        cls: bool,
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
    def cls(self) -> bool:
        """Return the class of the endpoint."""
        return self._cls

    @cls.setter
    def cls(self, cls: bool) -> None:
        """Validate and set the class."""
        if self._frozen:
            raise RuntimeError("Cannot set class on a frozen EndPoint")
        assert isinstance(cls, bool), f"Invalid class: {cls}"
        self._cls = cls

    @property
    def idx(self) -> int:
        """Return the index of the endpoint."""
        return self._idx

    @idx.setter
    def idx(self, idx: int) -> None:
        """Validate and set the index."""
        if self._frozen:
            raise RuntimeError("Cannot set index on a frozen EndPoint")
        assert isinstance(idx, int) and 0 <= idx < 256, f"Invalid index: {idx}"
        self._idx = idx

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
                    if not ref[0] in ROWS:
                        raise ValueError(f"Invalid reference row: {ref[0]}")
                    if not 0 <= int(ref[1:]) < 256:
                        raise ValueError(f"Invalid reference index: {ref[1:]}")
                r: str = ref[0]
                i = int(ref[1:])
            elif isinstance(ref, (list, tuple)) and len(ref) == 3:
                if _logger.isEnabledFor(level=DEBUG):
                    if not len(ref) == 2:
                        raise ValueError(f"Invalid reference sequence length: {len(ref)} != 2")
                    if not ref[0] in ROWS:
                        raise ValueError(f"Invalid reference row: {ref[0]}")
                    if not (isinstance(ref[1], int) and 0 <= ref[1] < 256):
                        raise ValueError(f"Invalid reference index: {ref[1]}")
                assert isinstance(ref[0], str), f"Invalid reference row type: {type(ref[0])}"
                assert isinstance(ref[1], int), f"Invalid reference index type: {type(ref[1])}"
                r: str = ref[0]
                i: int = ref[1]
            else:
                raise TypeError(f"Invalid reference type: {type(ref)}")
            self._refs.append([r, i])

    @property
    def row(self) -> Row:
        """Return the row of the endpoint."""
        return self._row

    @row.setter
    def row(self, row: Row) -> None:
        """Validate and set the row."""
        if self._frozen:
            raise RuntimeError("Cannot set row on a frozen EndPoint")
        if _logger.isEnabledFor(level=DEBUG) and not (row in ROWS):
            raise ValueError(f"Invalid row: {row}")
        self._row = row

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

    def __hash__(self) -> int:
        """Return the hash of the endpoint."""
        if self.is_frozen():
            # Hash is defined in self.freeze() to ensure immutability
            return self._hash
        # Else it is dynamically defined.
        return hash((self.row, self.idx, self.cls, self.typ, self.refs))

    def __str__(self) -> str:
        """Return the string representation of the endpoint."""
        return (
            f"EndPoint(row={self.row}, idx={self.idx}, cls={self.cls}"
            f", typ={self.typ}, refs=[{self.refs}])"
        )

    def copy(self, clean: bool = False) -> EndPoint:
        """Return a copy of the endpoint with no references."""
        return EndPoint(
            self.row, self.idx, self.cls, self.typ, [] if clean else self.refs, frozen=self._frozen
        )

    def freeze(self, _fo_visited_in_freeze_call: set[int] | None = None) -> None:
        """Freeze the endpoint, making it immutable."""
        if not self.is_frozen():
            # Need to make references immutable
            self.refs = ref_tuple_store.add(tuple(ref_store.add(tuple(ref)) for ref in self.refs))
            self._hash = hash((self.row, self.idx, self.cls, self.typ, self.refs))
            super().freeze()

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
                        all(ref[0] in CGT_VALID_SRC_ROWS[CGraphType.UNKNOWN] for ref in self.refs)
                        and self.cls == EndPointClass.DST
                    )
                    or self.cls == EndPointClass.SRC
                ):
                    raise ValueError(
                        "All destination endpoint references must be a valid source row."
                    )
                if not (
                    (
                        all(ref[0] in CGT_VALID_DST_ROWS[CGraphType.UNKNOWN] for ref in self.refs)
                        and self.cls == EndPointClass.SRC
                    )
                    or self.cls == EndPointClass.DST
                ):
                    raise ValueError(
                        "All source endpoint references must be a valid destination row."
                    )
                if not all(0 <= ref[1] < 256 for ref in self.refs if isinstance(ref[1], int)):
                    raise ValueError("All reference indices must be between 0 and 255.")

    def to_json(self) -> dict[str, str | int | list[list[str | int]]]:
        """Convert the endpoint to a JSON-compatible object."""
        return {
            "row": str(self.row),
            "idx": self.idx,
            "cls": self.cls,
            "typ": str(self.typ),
            "refs": [list(ref) for ref in self.refs],
        }
