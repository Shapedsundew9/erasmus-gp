"""End point and end point reference classes."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.egp_typing import EndPointClass, EndPointHash, EndPointIndex, EndPointType, Row


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenericEndPointABC(ABC):
    """Lowest common denominator end point class"""

    @abstractmethod
    def __init__(self, row: Row, idx: int) -> None:
        """Initialize the endpoint."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def cls(cls) -> type:
        """Return the object class type."""
        raise NotImplementedError

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the end point reference."""
        raise NotImplementedError

    @abstractmethod
    def get_idx(self) -> EndPointIndex:
        """Return the index of the end point."""
        raise NotImplementedError

    @abstractmethod
    def get_row(self) -> Row:
        """Return the row of the end point."""
        raise NotImplementedError

    @abstractmethod
    def json_obj(self) -> list[Any]:
        """Return a json serializable object."""
        raise NotImplementedError

    @abstractmethod
    def key_base(self) -> str:
        """Base end point hash."""
        raise NotImplementedError

    @abstractmethod
    def set_idx(self, idx: EndPointIndex) -> None:
        """Set the index of the end point."""
        raise NotImplementedError

    @abstractmethod
    def set_row(self, row: Row) -> None:
        """Set the row of the end point."""
        raise NotImplementedError

    @abstractmethod
    def verify(self) -> None:
        """Verify the end point reference."""
        raise NotImplementedError


class EndPointRefABC(GenericEndPointABC):
    """Defines the connection to a row in a Graph."""

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Equivilence for end point references."""
        raise NotImplementedError

    @abstractmethod
    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a key for this end point reference using EndPointClass cls.
        self.key_base() in self.force_key(cls) must be True.
        """
        raise NotImplementedError


class XEndPointRefABC(EndPointRefABC):
    """Specializes EndPointRefABC for Source and Destination variants."""

    @abstractmethod
    def key(self) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        raise NotImplementedError

    @abstractmethod
    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        raise NotImplementedError

    @abstractmethod
    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        raise NotImplementedError

    @abstractmethod
    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        raise NotImplementedError


class EndPointABC(XEndPointRefABC):
    """Defines an end point in a gc_graph."""

    @abstractmethod
    def __init__(self, row: Row, idx: int, typ: EndPointType,
            cls: EndPointClass, refs: list[XEndPointRefABC]) -> None:
        """Initialize the endpoint."""
        raise NotImplementedError

    @abstractmethod
    def _del_invalid_refs(self, ep: EndPointABC, row: Row, has_f: bool = False) -> None:
        """Remove any invalid references"""
        raise NotImplementedError

    @abstractmethod
    def as_ref(self) -> EndPointRefABC:
        """Return a reference to this end point."""
        raise NotImplementedError

    @abstractmethod
    def clean_copy(self) -> EndPointABC:
        """Return a copy of the end point with no references."""
        raise NotImplementedError

    @abstractmethod
    def copy(self, clean: bool = False) -> EndPointABC:
        """Return a copy of the end point with no references."""
        raise NotImplementedError

    @abstractmethod
    def get_typ(self) -> EndPointType:
        """Return the type of the end point."""
        raise NotImplementedError

    @abstractmethod
    def get_cls(self) -> EndPointClass:
        """Return the class of the end point."""
        raise NotImplementedError

    @abstractmethod
    def get_refs(self) -> list[XEndPointRefABC]:
        """Return the references of the end point."""
        raise NotImplementedError

    @abstractmethod
    def move_cls_copy(self, row: Row, cls: EndPointClass) -> EndPointABC:
        """Return a copy of the end point with the row & cls changed."""
        raise NotImplementedError

    @abstractmethod
    def move_copy(self, row: Row, clean: bool = False, has_f: bool = False) -> EndPointABC:
        """Return a copy of the end point with the row changed.
        Any references that are no longer valid are deleted.
        """
        raise NotImplementedError

    @abstractmethod
    def redirect_refs(self, old_ref_row, new_ref_row) -> None:
        """Redirect all references to old_ref_row to new_ref_row."""
        raise NotImplementedError

    @abstractmethod
    def safe_add_ref(self, ref: XEndPointRefABC) -> None:
        """Check endpoint has a reference before adding it."""
        raise NotImplementedError

    @abstractmethod
    def set_typ(self, typ: EndPointType) -> None:
        """Set the type of the end point."""
        raise NotImplementedError

    @abstractmethod
    def set_cls(self, cls: EndPointClass) -> None:
        """Set the class of the end point."""
        raise NotImplementedError

    @abstractmethod
    def set_refs(self, refs: list[XEndPointRefABC]) -> None:
        """Set the references of the end point."""
        raise NotImplementedError
