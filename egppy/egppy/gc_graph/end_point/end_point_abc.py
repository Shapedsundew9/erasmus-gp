"""End point and end point reference classes."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Self
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


class EndPointRefABC(GenericEndPointABC):
    """Defines the connection to a row in an InternalGraph."""

    def __eq__(self, other: object) -> bool:
        """Equivilence for end point references."""
        raise NotImplementedError

    def __hash__(self) -> int:
        """For hashable operations."""
        raise NotImplementedError

    def force_key(self, cls: EndPointClass) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        raise NotImplementedError

    def key(self) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        raise NotImplementedError

    def invert_key(self) -> EndPointHash:
        """Invert hash. Return a hash for the source/destination endpoint equivilent."""
        raise NotImplementedError


class EndPointABC(GenericEndPointABC):
    """Defines an end point in a gc_graph."""

    @abstractmethod
    def __hash__(self) -> int:
        """For hashable operations."""
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
    def copy(self, clean: bool = False) -> Self:
        """Return a copy of the end point with no references."""
        raise NotImplementedError

    @abstractmethod
    def force_key(self, force_class: EndPointClass | None = None) -> EndPointHash:
        """Create a unique key to use in the internal graph forcing the class type."""
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
    def get_refs(self) -> list[EndPointRefABC]:
        """Return the references of the end point."""
        raise NotImplementedError

    @abstractmethod
    def is_dst(self) -> bool:
        """Return True if the end point is a destination."""
        raise NotImplementedError
    
    @abstractmethod
    def is_src(self) -> bool:
        """Return True if the end point is a source."""
        raise NotImplementedError

    @abstractmethod
    def key(self) -> EndPointHash:
        """Create a unique key to use in the internal graph."""
        raise NotImplementedError

    @abstractmethod
    def move_cls_copy(self, row: Row, cls: EndPointClass) -> EndPointABC:
        """Return a copy of the end point with the row & cls changed."""
        raise NotImplementedError

    @abstractmethod
    def move_copy(self, row: Row, clean: bool = False, has_f: bool = False) -> Self:
        """Return a copy of the end point with the row changed.
        Any references that are no longer valid are deleted.
        """
        raise NotImplementedError

    @abstractmethod
    def redirect_refs(self, old_ref_row, new_ref_row) -> None:
        """Redirect all references to old_ref_row to new_ref_row."""
        raise NotImplementedError

    @abstractmethod
    def safe_add_ref(self, ref: EndPointRefABC) -> None:
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
    def set_refs(self, refs: list[EndPointRefABC]) -> None:
        """Set the references of the end point."""
        raise NotImplementedError
