"""Endpoint class using builtin collections."""

from __future__ import annotations

from typing import Any

from egpcommon.common_obj_mixin import CommonObjMixin
from egpcommon.properties import CGraphType
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.end_point.end_point_abc import GenericEndPointABC
from egppy.c_graph.end_point.end_point_abc import EndPointABC, XEndPointRefABC
from egppy.c_graph.c_graph_constants import (
    DESTINATION_ROWS,
    EPC_STR_TUPLE,
    ROWS,
    SOURCE_ROWS,
    SrcRow,
)
from egppy.c_graph.c_graph_constants import DstRow, EndPointClass, EndPointHash, Row
from egppy.c_graph.c_graph_validation import valid_dst_rows, valid_src_rows


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class EndPointMixin(CommonObjMixin):
    """Mixin methods for EndPoint."""

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        if not isinstance(other, self.__class__):
            return False
        return (
            self.get_row() == other.get_row()
            and self.get_idx() == other.get_idx()
            and self.get_typ() == other.get_typ()
            and self.get_cls() == other.get_cls()
            and self.get_refs() == other.get_refs()
        )

    def __hash__(self) -> int:
        """Return the hash of the endpoint."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        return hash(
            (self.get_row(), self.get_idx(), self.get_typ(), self.get_cls(), hash(self.get_refs()))
        )

    def del_invalid_refs(self, cgt: CGraphType) -> None:
        """Remove any invalid references"""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        row = self.get_row()
        valid_ref_rows: frozenset = (
            valid_dst_rows(cgt)[row] if isinstance(row, SrcRow) else valid_src_rows(cgt)[row]
        )
        erefs = enumerate(self.get_refs())
        for vidx in reversed([i for i, r in erefs if r.get_row() not in valid_ref_rows]):
            del self.get_refs()[vidx]

    @classmethod
    def cls(cls) -> type:
        """Return the object class type."""
        raise NotImplementedError

    def consistency(self) -> bool:
        """Check the consistency of the end point."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        if self.is_src():
            assert list(self.get_refs()) == list(set(self.get_refs())), "Duplicate references."
        return super().consistency()

    def copy(self, clean: bool = False) -> EndPointABC:
        """Return a copy of the end point with no references."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        return self.cls()(
            self.get_row(),
            self.get_idx(),
            self.get_typ(),
            self.get_cls(),
            [] if clean else self.get_refs(),
        )

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        return self.key_base() + EPC_STR_TUPLE[not self.get_cls()]

    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        return self.get_cls() == EndPointClass.DST

    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        return self.get_cls() == EndPointClass.SRC

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        return self.key_base() + EPC_STR_TUPLE[self.get_cls()]

    def move_cls_copy(self, row: Row, cls: EndPointClass) -> EndPointABC:
        """Return a copy of the end point with the row & cls changed.
        If the class of the endpoint has changed then the references must
        be invalid and are not copied."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        if _LOG_DEBUG:
            if cls == EndPointClass.SRC:
                assert row in SOURCE_ROWS, "Invalid row for source endpoint"
            else:
                assert row in DESTINATION_ROWS, "Invalid row for destination endpoint"
        return self.cls()(row, self.get_idx(), self.get_typ(), cls, [])

    def move_copy(
        self, row: Row, clean: bool = False, cgt: CGraphType = CGraphType.STANDARD
    ) -> EndPointABC:
        """Return a copy of the end point with the row changed.
        Any references that are no longer valid are deleted."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        if _LOG_DEBUG:
            if self.get_cls() == EndPointClass.SRC:
                assert row in SOURCE_ROWS, "Cannot change cls from SRC to DST in a move_copy."
            else:
                assert row in DESTINATION_ROWS, "Cannot change cls from DST to SRC in a move_copy."
        ep: EndPointABC = self.copy(clean)
        ep.set_row(row)
        if not clean:
            ep.del_invalid_refs(cgt)
        return ep

    def redirect_refs(self, old_ref_row, new_ref_row) -> None:
        """Redirect all references to old_ref_row to new_ref_row."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        for ref in (x.get_row() == old_ref_row for x in self.get_refs()):
            ref.set_row(new_ref_row)

    def safe_add_ref(self, ref: XEndPointRefABC) -> None:
        """Check if a reference exists before adding it."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        if ref not in self.get_refs():
            _logger.warning("Adding reference %s to %s: This is inefficient.", ref, self)
            self.get_refs().append(ref)

    def verify(self) -> bool:
        """Verify the end point."""
        assert isinstance(self, EndPointABC), f"Invalid type: {type(self)}"
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        if self.is_dst():
            assert self.get_row() in DESTINATION_ROWS, f"Invalid destination row: {self.get_row()}"
            if self.get_row() == DstRow.F:
                assert self.get_idx() == 0, f"Invalid index for row F: {self.get_idx()}"
            refs = self.get_refs()
            assert len(refs) == 1, f"Invalid number of references for dst endpoint: {len(refs)}"
            assert refs[0].is_src(), f"Invalid source reference: {refs[0]}"
            refs[0].verify()
        if self.is_src():
            assert self.get_row() in SOURCE_ROWS, f"Invalid source row: {self.get_row()}"
            for ref in self.get_refs():
                assert ref.is_dst(), f"Invalid destination reference: {ref}"
                ref.verify()
        return super().verify()
