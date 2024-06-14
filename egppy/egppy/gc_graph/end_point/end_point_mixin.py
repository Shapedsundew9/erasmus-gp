"""Endpoint class using builtin collections."""
from __future__ import annotations
from typing import Self
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.egp_typing import (EndPointClass, Row, EndPointHash, EndPointType,
    VALID_ROW_DESTINATIONS as VRD, VALID_ROW_SOURCES as VRS, DST_EP, SRC_EP, SOURCE_ROWS,
    DESTINATION_ROWS)
from egppy.gc_graph.end_point.end_point_abc import EndPointABC, EndPointRefABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenericEndPointMixin():
    """Mixin methods for GenericEndPoint."""

    def __repr__(self) -> str:
        """Return a string representation of the endpoint."""
        return f"{self.__class__.__name__}(row={self.get_row()}, idx={self.get_idx()})"

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def json_obj(self) -> list[str | int]:
        """Return a json serializable object."""
        return [self.get_row(), self.get_idx()]

    def key_base(self) -> str:
        """Base end point hash."""
        return f"{self.get_row()}_{self.get_idx()}"


class EndPointRefMixin():
    """Mixin methods for EndPointRef."""

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if not isinstance(other, self.__class__):
            return False
        return self.get_row() == other.get_row() and self.get_idx() == other.get_idx()

    def __hash__(self) -> int:
        """Return the hash of the end point."""
        return hash(self.key())

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        return self.key_base() + "ds"[cls]

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        raise NotImplementedError

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError


class DstEndPointRefMixin():
    """Mixin methods for DstEndPointRef."""

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + "d"

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        return self.key_base() + "s"


class SrcEndPointRefMixin():
    """Mixin methods for SrcEndPointRef."""

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + "s"

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        return self.key_base() + "d"


class EndPointMixin():
    """Mixin methods for EndPoint."""

    def __init__(self, *args) -> None:
        """Initialize the endpoint."""
        raise NotImplementedError

    def __hash__(self) -> int:
        """Return the hash of the end point."""
        return hash(self.key())

    def _del_invalid_refs(self, ep: EndPointABC, row: Row, has_f: bool = False) -> None:
        """Remove any invalid references"""
        valid_ref_rows: tuple[Row, ...] = VRS[has_f][row] if ep.is_dst() else VRD[has_f][row]
        erefs = enumerate(ep.get_refs())
        for vidx in reversed([i for i, r in erefs if r.get_row() not in valid_ref_rows]):
            del ep.get_refs()[vidx]

    def copy(self, clean: bool = False) -> Self:
        """Return a copy of the end point with no references."""
        return self.__class__(self.get_row(), self.get_idx(), self.get_typ(), self.get_cls(),
            [] if clean else self.get_refs())

    def get_cls(self) -> EndPointClass:
        """Return the class of the end point."""
        raise NotImplementedError

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_refs(self) -> list[EndPointRefABC]:
        """Return the references of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def get_typ(self) -> EndPointType:
        """Return the type of the end point."""
        raise NotImplementedError

    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        return self.get_cls() == DST_EP

    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        return self.get_cls() == SRC_EP

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        raise NotImplementedError

    def move_copy(self, row: Row, clean: bool = False, has_f: bool = False) -> Self:
        """Return a copy of the end point with the row changed.
        Any references that are no longer valid are deleted."""
        ep: Self = self.copy(clean)
        ep.set_row(row)
        if not clean:
            self._del_invalid_refs(ep, row, has_f)  # type: ignore
        return ep

    def move_cls_copy(self, row: Row, cls: EndPointClass) -> Self:
        """Return a copy of the end point with the row & cls changed.
        If the class of the endpoint has changed then the references must
        be invalid and are not copied."""
        if _LOG_DEBUG:
            if cls == SRC_EP:
                assert row in SOURCE_ROWS, "Invalid row for source endpoint"
            else:
                assert row in DESTINATION_ROWS, "Invalid row for destination endpoint"
        return self.__class__(row, self.get_idx(), self.get_typ(), self.get_cls(), [])

    def redirect_refs(self, old_ref_row, new_ref_row) -> None:
        """Redirect all references to old_ref_row to new_ref_row."""
        for ref in (x.get_row() == old_ref_row for x in self.get_refs()):
            ref.set_row(new_ref_row)

    def set_row(self, row: Row) -> None:
        """Set the row of the end point."""
        raise NotImplementedError
