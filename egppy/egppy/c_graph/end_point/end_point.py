"""Endpoint class using builtin collections."""

from __future__ import annotations
from calendar import c
from typing import Final

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.common_obj import CommonObj
from egpcommon.common import JSONDictType

from egppy.c_graph.end_point.end_point_abc import (
    EndPointABC,
    EndPointRefABC,
    GenericEndPointABC,
    XEndPointRefABC,
)
from egppy.c_graph.end_point.end_point_mixin import EndPointMixin
from egppy.c_graph.c_graph_constants import (
    DESTINATION_ROWS,
    EPC_STR_TUPLE,
    ROWS,
    SOURCE_ROWS,
    DstRow,
    EndPointClass,
    EndPointHash,
    Row,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenericEndPoint(CommonObj, GenericEndPointABC):
    """Endpoint class using builtin collections."""

    __slots__ = ("__row", "__idx", "__weakref__")

    def __init__(self, row: Row, idx: int) -> None:
        """Initialize the endpoint."""
        self.__row: Final[Row] = row
        self.__idx: Final[int] = idx
        assert self.verify(), f"Invalid generic endpoint: {self}"
        assert self.consistency(), f"Inconsistent generic endpoint: {self}"

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if isinstance(other, self.__class__):
            return self.__row == other.row and self.__idx == other.idx
        if isinstance(other, (tuple, list)):
            return self.__row == other[0] and self.__idx == other[1]
        return False

    def __hash__(self) -> int:
        """Return the hash of the endpoint."""
        return hash((self.__row, self.__idx))

    def __repr__(self) -> str:
        """Return a string representation of the endpoint."""
        sorted_members = sorted(self.to_json().items(), key=lambda x: x[0])
        return f"{self.cls().__name__}({', '.join((k + '=' + str(v) for k, v in sorted_members))})"

    @property
    def idx(self) -> int:
        """Return the index of the end point."""
        return self.__idx

    @property
    def row(self) -> Row:
        """Return the row of the end point."""
        return self.__row

    def cls(self) -> type:
        """Return the object class type."""
        return self.__class__

    def to_json(self) -> JSONDictType:
        """Return a json serializable object."""
        return {
            "row": self.__row,
            "idx": self.__idx,
        }

    def verify(self) -> bool:
        """Verify the end point."""
        assert self.__row in ROWS, f"Invalid row: {self.__row}"
        assert self.__idx >= 0, f"Invalid index: {self.__idx}"
        assert self.__idx < 2**8, f"Invalid index: {self.__idx}"
        return super().verify()


class EndPointRef(GenericEndPoint, EndPointRefABC):
    """Refers to an end point."""

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        return self.key_base() + EPC_STR_TUPLE[cls]


class DstEndPointRef(EndPointRef, XEndPointRefABC):
    """Refers to a destination end point."""

    def copy(self) -> XEndPointRefABC:
        """Return a copy of the end point."""
        return self.cls()(self.__row, self.__idx)

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + "d"

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        return self.key_base() + "s"

    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        return True

    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        return False

    def verify(self) -> bool:
        """Verify the end point."""
        assert self.row in DESTINATION_ROWS, f"Invalid destination row: {self.row}"
        if self.__row == DstRow.F:
            assert self.__idx == 0, f"Invalid index for row F: {self.__idx}"
        return super().verify()


class SrcEndPointRef(EndPointRef, XEndPointRefABC):
    """Refers to a source end point."""

    def copy(self) -> XEndPointRefABC:
        """Return a copy of the end point."""
        return self.cls()(self.__row, self.__idx)

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + "s"

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        return self.key_base() + "d"

    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        return False

    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        return True

    def verify(self) -> bool:
        """Verify the end point."""
        assert self.__row in SOURCE_ROWS, f"Invalid source row: {self.row}"
        assert self.__idx >= 0, f"Invalid index: {self.idx}"
        assert self.__idx < 2**8, f"Invalid index: {self.idx}"
        return super().verify()


class EndPoint(EndPointRef, EndPointMixin, EndPointABC):
    """Endpoint class using builtin collections."""

    __slots__ = ("_typ", "_cls", "_refs")

    def __init__(
        self, row: Row, idx: int, typ: int, cls: EndPointClass, refs: list[XEndPointRefABC]
    ) -> None:
        """Initialize the endpoint."""
        super().__init__(row=row, idx=idx)
        self._typ: int = typ
        self._cls: EndPointClass = cls
        self._refs: list[XEndPointRefABC] = list(refs)

    def as_ref(self) -> EndPointRefABC:
        """Return a reference to this end point."""
        ref_cls = SrcEndPointRef if self.is_src() else DstEndPointRef
        return ref_cls(self.__row, self.__idx)

    def get_typ(self) -> int:
        """Return the type of the end point."""
        return self._typ

    def get_cls(self) -> EndPointClass:
        """Return the class of the end point."""
        return self._cls

    def get_refs(self) -> list[XEndPointRefABC]:
        """Return the references of the end point."""
        return self._refs

    def set_typ(self, typ: int) -> None:
        """Set the type of the end point."""
        self._typ = typ

    def set_cls(self, cls: EndPointClass) -> None:
        """Set the class of the end point."""
        self._cls = cls

    def set_refs(self, refs: list[XEndPointRefABC]) -> None:
        """Set the references of the end point."""
        self._refs = refs.copy()
