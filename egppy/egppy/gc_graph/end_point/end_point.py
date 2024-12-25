"""Endpoint class using builtin collections."""

from __future__ import annotations

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.end_point_abc import (
    EndPointABC,
    EndPointRefABC,
    GenericEndPointABC,
    XEndPointRefABC,
)
from egppy.gc_graph.end_point.end_point_mixin import EndPointMixin, GenericEndPointMixin
from egppy.gc_graph.end_point.end_point_type import EndPointType
from egppy.gc_graph.typing import (
    DESTINATION_ROWS,
    EP_CLS_STR_TUPLE,
    ROWS,
    SOURCE_ROWS,
    DestinationRow,
    EndPointClass,
    EndPointHash,
    Row,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenericEndPoint(GenericEndPointMixin, GenericEndPointABC):
    """Endpoint class using builtin collections."""

    def __init__(self, row: Row, idx: int) -> None:
        """Initialize the endpoint."""
        self._row: Row = row
        self._idx: int = idx

    def get_idx(self) -> int:
        """Return the index of the end point."""
        return self._idx

    def get_row(self) -> Row:
        """Return the row of the end point."""
        return self._row

    def set_idx(self, idx: int) -> None:
        """Set the index of the end point."""
        self._idx = idx

    def set_row(self, row: Row) -> None:
        """Set the row of the end point."""
        self._row = row


class EndPointRef(GenericEndPoint, EndPointRefABC):
    """Refers to an end point."""

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if not isinstance(other, (EndPointRef, DstEndPointRef, SrcEndPointRef)):
            return self._eq_to_seq(other)
        return self.get_row() == other.get_row() and self.get_idx() == other.get_idx()

    def _eq_to_seq(self, other: object) -> bool:
        """Compare the end point to a sequence."""
        if not isinstance(other, (tuple, list)):
            return False
        if len(other) != 2:
            return False
        if not isinstance(other[0], Row) or not isinstance(other[1], int):
            return False
        return self.get_row() == other[0] and self.get_idx() == other[1]

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        return self.key_base() + EP_CLS_STR_TUPLE[cls]

    def verify(self) -> None:
        """Verify the end point."""
        assert self.get_row() in ROWS, f"Invalid row: {self.get_row()}"
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        super().verify()


class DstEndPointRef(EndPointRef, XEndPointRefABC):
    """Refers to a destination end point."""

    def copy(self) -> XEndPointRefABC:
        """Return a copy of the end point."""
        return self.cls()(self._row, self._idx)

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

    def verify(self) -> None:
        """Verify the end point."""
        assert self.get_row() in DESTINATION_ROWS, f"Invalid destination row: {self.get_row()}"
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        if self.get_row() == DestinationRow.F:
            assert self.get_idx() == 0, f"Invalid index for row F: {self.get_idx()}"
        super().verify()


class SrcEndPointRef(EndPointRef, XEndPointRefABC):
    """Refers to a source end point."""

    def copy(self) -> XEndPointRefABC:
        """Return a copy of the end point."""
        return self.cls()(self._row, self._idx)

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

    def verify(self) -> None:
        """Verify the end point."""
        assert self.get_row() in SOURCE_ROWS, f"Invalid source row: {self.get_row()}"
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        super().verify()


class EndPoint(EndPointRef, EndPointMixin, EndPointABC):
    """Endpoint class using builtin collections."""

    def __init__(
        self, row: Row, idx: int, typ: EndPointType, cls: EndPointClass, refs: list[XEndPointRefABC]
    ) -> None:
        """Initialize the endpoint."""
        super().__init__(row=row, idx=idx)
        self._typ: EndPointType = typ
        self._cls: EndPointClass = cls
        self._refs: list[XEndPointRefABC] = list(refs)

    def as_ref(self) -> EndPointRefABC:
        """Return a reference to this end point."""
        ref_cls = SrcEndPointRef if self.is_src() else DstEndPointRef
        return ref_cls(self._row, self._idx)

    def get_typ(self) -> EndPointType:
        """Return the type of the end point."""
        return self._typ

    def get_cls(self) -> EndPointClass:
        """Return the class of the end point."""
        return self._cls

    def get_refs(self) -> list[XEndPointRefABC]:
        """Return the references of the end point."""
        return self._refs

    def set_typ(self, typ: EndPointType) -> None:
        """Set the type of the end point."""
        self._typ = typ

    def set_cls(self, cls: EndPointClass) -> None:
        """Set the class of the end point."""
        self._cls = cls

    def set_refs(self, refs: list[XEndPointRefABC]) -> None:
        """Set the references of the end point."""
        self._refs = refs.copy()
