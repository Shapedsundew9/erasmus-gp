"""Endpoint class using builtin collections."""
from __future__ import annotations
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.end_point.end_point_abc import (EndPointRefABC, GenericEndPointABC,
    EndPointABC)
from egppy.gc_graph.end_point.end_point_mixin import (GenericEndPointMixin, EndPointRefMixin,
    DstEndPointRefMixin, SrcEndPointRefMixin, EndPointMixin)
from egppy.gc_graph.egp_typing import EndPointClass, EndPointHash, EndPointIndex, EndPointType, Row


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class BuiltinGenericEndPoint(GenericEndPointMixin, GenericEndPointABC):
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


class BuiltinEndPointRef(BuiltinGenericEndPoint, EndPointRefMixin, EndPointRefABC):
    """Refers to an end point."""


class BuiltinDstEndPointRef(BuiltinEndPointRef, DstEndPointRefMixin):
    """Refers to a destination end point."""


class BuiltinSrcEndPointRef(BuiltinEndPointRef, SrcEndPointRefMixin):
    """Refers to a source end point."""


class BuiltInEndPoint(BuiltinGenericEndPoint, EndPointMixin, EndPointABC):
    """Endpoint class using builtin collections."""

    def __init__(self, row: Row, idx: int, typ: EndPointType,
            cls: EndPointClass, refs: list[EndPointRefABC]) -> None:
        """Initialize the endpoint."""
        super().__init__(row=row, idx=idx)
        self._typ: EndPointType = typ
        self._cls: EndPointClass = cls
        self._refs: list[EndPointRefABC] = refs.copy()

    def as_ref(self) -> EndPointRefABC:
        """Return a reference to this end point."""
        return BuiltinEndPointRef(self._row, self._idx)

    def get_typ(self) -> EndPointType:
        """Return the type of the end point."""
        return self._typ

    def get_cls(self) -> EndPointClass:
        """Return the class of the end point."""
        return self._cls

    def get_refs(self) -> list[EndPointRefABC]:
        """Return the references of the end point."""
        return self._refs

    def set_typ(self, typ: EndPointType) -> None:
        """Set the type of the end point."""
        self._typ = typ

    def set_cls(self, cls: EndPointClass) -> None:
        """Set the class of the end point."""
        self._cls = cls

    def set_refs(self, refs: list[EndPointRefABC]) -> None:
        """Set the references of the end point."""
        self._refs = refs.copy()
