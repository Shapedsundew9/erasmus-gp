"""Endpoint class using builtin collections."""
from __future__ import annotations
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.common.common_obj_mixin import CommonObjMixin
from egppy.gc_graph.egp_typing import (DestinationRow, Row, EndPointHash, EndPointType,
    EndPointClass, VALID_ROW_DESTINATIONS as VRD, VALID_ROW_SOURCES as VRS, SOURCE_ROWS, ROWS,
    DESTINATION_ROWS, EP_CLS_STR_TUPLE)
from egppy.gc_graph.ep_type import validate
from egppy.gc_graph.end_point.end_point_abc import EndPointABC, XEndPointRefABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenericEndPointMixin(CommonObjMixin):
    """Mixin methods for GenericEndPoint."""

    def __repr__(self) -> str:
        """Return a string representation of the endpoint."""
        sorted_members = sorted(self.json_obj().items(), key=lambda x: x[0])
        return f"{self.cls().__name__}({', '.join((k + '=' + str(v) for k, v in sorted_members))})"

    @classmethod
    def cls(cls) -> type:
        """Return the object class type."""
        return cls

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def json_obj(self) -> dict[str, Any]:
        """Return a json serializable object."""
        # return  a dictionary of the return of each method starting with
        # "get_" where the key is the method name without the "get_"
        return {k: v for k, v in self.__dict__.items()}

    def key_base(self) -> str:
        """Base end point hash."""
        return f"{self.get_row()}{self.get_idx()}"

    def verify(self) -> None:
        """Verify the end point."""
        assert self.get_row() in ROWS, f"Invalid row: {self.get_row()}"
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        super().verify()


class EndPointRefMixin(CommonObjMixin):
    """Mixin methods for EndPointRef."""

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if not isinstance(other, self.__class__):
            return False
        return self.get_row() == other.get_row() and self.get_idx() == other.get_idx()

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        return self.key_base() + EP_CLS_STR_TUPLE[cls]

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

    def verify(self) -> None:
        """Verify the end point."""
        assert self.get_row() in ROWS, f"Invalid row: {self.get_row()}"
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        super().verify()


class DstEndPointRefMixin(CommonObjMixin):
    """Mixin methods for DstEndPointRef."""

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if not isinstance(other, self.__class__):
            return False
        return self.get_row() == other.get_row() and self.get_idx() == other.get_idx()

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        return self.key_base() + EP_CLS_STR_TUPLE[cls]

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + "d"

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

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


class SrcEndPointRefMixin(CommonObjMixin):
    """Mixin methods for SrcEndPointRef."""

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if not isinstance(other, self.__class__):
            return False
        return self.get_row() == other.get_row() and self.get_idx() == other.get_idx()

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        return self.key_base() + EP_CLS_STR_TUPLE[cls]

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + "s"

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

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


class EndPointMixin(CommonObjMixin):
    """Mixin methods for EndPoint."""

    def __init__(self, *args) -> None:
        """Initialize the endpoint."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Compare two end points."""
        if not isinstance(other, self.__class__):
            return False
        return self.get_row() == other.get_row() and self.get_idx() == other.get_idx() \
            and self.get_typ() == other.get_typ() and self.get_cls() == other.get_cls() \
            and self.get_refs() == other.get_refs()

    def del_invalid_refs(self, has_f: bool = False) -> None:
        """Remove any invalid references"""
        row = self.get_row()
        valid_ref_rows: tuple[Row, ...] = VRS[has_f][row] if self.is_dst() else VRD[has_f][row]
        erefs = enumerate(self.get_refs())
        for vidx in reversed([i for i, r in erefs if r.get_row() not in valid_ref_rows]):
            del self.get_refs()[vidx]

    @classmethod
    def cls(cls) -> type:
        """Return the object class type."""
        raise NotImplementedError

    def consistency(self) -> None:
        """Check the consistency of the end point."""
        if self.is_src():
            assert list(self.get_refs()) == list(set(self.get_refs())), "Duplicate references."
        super().consistency()

    def copy(self, clean: bool = False) -> EndPointABC:
        """Return a copy of the end point with no references."""
        return self.cls()(self.get_row(), self.get_idx(), self.get_typ(), self.get_cls(),
            [] if clean else self.get_refs())

    def get_cls(self) -> EndPointClass:
        """Return the class of the end point."""
        raise NotImplementedError

    def get_idx(self) -> int:
        """Return the index of the end point."""
        raise NotImplementedError

    def get_refs(self) -> list[XEndPointRefABC]:
        """Return the references of the end point."""
        raise NotImplementedError

    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    def get_typ(self) -> EndPointType:
        """Return the type of the end point."""
        raise NotImplementedError

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        return self.key_base() + EP_CLS_STR_TUPLE[not self.get_cls()]

    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        return self.get_cls() == EndPointClass.DST

    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        return self.get_cls() == EndPointClass.SRC

    def key(self) -> EndPointHash:
        """Return the key of the end point."""
        return self.key_base() + EP_CLS_STR_TUPLE[self.get_cls()]

    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

    def move_cls_copy(self, row: Row, cls: EndPointClass) -> EndPointABC:
        """Return a copy of the end point with the row & cls changed.
        If the class of the endpoint has changed then the references must
        be invalid and are not copied."""
        if _LOG_DEBUG:
            if cls == EndPointClass.SRC:
                assert row in SOURCE_ROWS, "Invalid row for source endpoint"
            else:
                assert row in DESTINATION_ROWS, "Invalid row for destination endpoint"
        return self.cls()(row, self.get_idx(), self.get_typ(), cls, [])

    def move_copy(self, row: Row, clean: bool = False, has_f: bool = False) -> EndPointABC:
        """Return a copy of the end point with the row changed.
        Any references that are no longer valid are deleted."""
        if _LOG_DEBUG:
            if self.cls == EndPointClass.SRC:
                assert row in SOURCE_ROWS, "Cannot change cls from SRC to DST in a move_copy."
            else:
                assert row in DESTINATION_ROWS, "Cannot change cls from DST to SRC in a move_copy."
        ep: EndPointABC = self.copy(clean)
        ep.set_row(row)
        if not clean:
            ep.del_invalid_refs(has_f)
        return ep

    def redirect_refs(self, old_ref_row, new_ref_row) -> None:
        """Redirect all references to old_ref_row to new_ref_row."""
        for ref in (x.get_row() == old_ref_row for x in self.get_refs()):
            ref.set_row(new_ref_row)

    def safe_add_ref(self, ref: XEndPointRefABC) -> None:
        """Check if a reference exists before adding it."""
        if ref not in self.get_refs():
            _logger.warning("Adding reference %s to %s: This is inefficient.", ref, self)
            self.get_refs().append(ref)

    def set_row(self, row: Row) -> None:
        """Set the row of the end point."""
        raise NotImplementedError

    def verify(self) -> None:
        """Verify the end point."""
        assert self.get_idx() >= 0, f"Invalid index: {self.get_idx()}"
        assert self.get_idx() < 2**8, f"Invalid index: {self.get_idx()}"
        assert validate(self.get_typ()), f"Invalid type: {self.get_typ()}"
        if self.is_dst():
            assert self.get_row() in DESTINATION_ROWS, f"Invalid destination row: {self.get_row()}"
            if self.get_row() == DestinationRow.F:
                assert self.get_idx() == 0, f"Invalid index for row F: {self.get_idx()}"
            refs = self.get_refs()
            assert len(refs) ==1, f"Invalid number of references for dst endpoint: {len(refs)}"
            assert refs[0].is_src(), f"Invalid source reference: {refs[0]}"
            refs[0].verify()
        if self.is_src():
            assert self.get_row() in SOURCE_ROWS, f"Invalid source row: {self.get_row()}"
            for ref in self.get_refs():
                assert ref.is_dst(), f"Invalid destination reference: {ref}"
                ref.verify()
        super().verify()
