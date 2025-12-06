"""
Abstract Base Class for Interface.

This module defines the abstract interface that all Interface implementations
must adhere to. It establishes the contract for interface operations while allowing
for different concrete implementations.

The abstract base class ensures consistency in the API across different interface types
and implementations while maintaining the flexibility to optimize specific variants.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Iterator, MutableSequence, Sequence

from egpcommon.common_obj_abc import CommonObjABC
from egppy.genetic_code.c_graph_constants import EPCls, Row
from egppy.genetic_code.endpoint_abc import EndPointABC, FrozenEndPointABC
from egppy.genetic_code.types_def import TypesDef


class FrozenInterfaceABC(CommonObjABC, Sequence, metaclass=ABCMeta):
    """Abstract Base Class for Immutable Interface.

    This class defines the essential interface that all Interface
    implementations must provide. It inherits CommonObjABC for validation methods
    and Sequence for immutable sequence operations.

    Interfaces define collections of endpoints that represent connections in
    genetic code, either as sources (inputs) or destinations (outputs).
    """

    __slots__ = ()

    # Abstract Comparison Methods

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        """Check equality of Interface instances.

        Args:
            value: Object to compare with.

        Returns:
            True if equal, False otherwise.
        """
        raise NotImplementedError("FrozenInterfaceABC.__eq__ must be overridden")

    # Abstract Container Protocol Methods

    @abstractmethod
    def __getitem__(self, idx: int) -> FrozenEndPointABC:  # type: ignore[override]
        """Get an endpoint by index.

        Args:
            idx: The index of the endpoint to retrieve.

        Returns:
            The EndPoint at the specified index.

        Raises:
            IndexError: If idx is out of range.
        """
        raise NotImplementedError("FrozenInterfaceABC.__getitem__ must be overridden")

    @abstractmethod
    def __hash__(self) -> int:
        """Return the hash of the interface.

        Returns:
            Hash value for the interface.
        """
        raise NotImplementedError("FrozenInterfaceABC.__hash__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Iterator[FrozenEndPointABC]:
        """Return an iterator over the endpoints.

        Returns:
            Iterator over EndPoint objects in the interface.
        """
        raise NotImplementedError("FrozenInterfaceABC.__iter__ must be overridden")

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of endpoints in the interface.

        Returns:
            Number of endpoints in this interface.
        """
        raise NotImplementedError("FrozenInterfaceABC.__len__ must be overridden")

    # Abstract String Representation

    @abstractmethod
    def __str__(self) -> str:
        """Return the string representation of the interface.

        Returns:
            String representation of the interface.
        """
        raise NotImplementedError("FrozenInterfaceABC.__str__ must be overridden")

    # Abstract Property Methods

    @abstractmethod
    def cls(self) -> EPCls:
        """Return the class of the interface.

        Returns:
            The EndPointClass (SRC or DST) of this interface.
        """
        raise NotImplementedError("FrozenInterfaceABC.cls must be overridden")

    @abstractmethod
    def sorted_unique_td_uids(self) -> list[int]:
        """Return the sorted unique type definition UIDs.

        Returns:
            Sorted list of unique TypesDef UIDs.
        """
        raise NotImplementedError("FrozenInterfaceABC.ordered_td_uids must be overridden")

    # Abstract Data Export Methods

    @abstractmethod
    def to_json(self, json_c_graph: bool = False) -> list:
        """Convert the interface to a JSON-compatible object.

        Args:
            json_c_graph: If True, returns a list suitable for JSON Connection Graph format.

        Returns:
            List of JSON-compatible endpoint representations.
        """
        raise NotImplementedError("FrozenInterfaceABC.to_json must be overridden")

    @abstractmethod
    def to_td(self) -> tuple[TypesDef, ...]:
        """Convert the interface to a tuple of TypesDef objects.

        Returns:
            Tuple of TypesDef objects for each endpoint.
        """
        raise NotImplementedError("FrozenInterfaceABC.to_td must be overridden")

    @abstractmethod
    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints).

        Returns:
            Sequence (tuple or list) of TypesDef UIDs for each endpoint.
        """
        raise NotImplementedError("FrozenInterfaceABC.to_td_uids must be overridden")

    @abstractmethod
    def types_and_indices(self) -> tuple[list[int], bytes]:
        """Return a tuple of the sorted unique type UIDs and the indices into it.

        Returns:
            Tuple of (sorted_unique_type_uids, byte_indices).
        """
        raise NotImplementedError("FrozenInterfaceABC.types must be overridden")

    @abstractmethod
    def unconnected_eps(self) -> list[FrozenEndPointABC]:
        """Return a list of unconnected endpoints.

        Returns:
            List of EndPoint objects that have no connections.
        """
        raise NotImplementedError("FrozenInterfaceABC.unconnected_eps must be overridden")


class InterfaceABC(FrozenInterfaceABC, MutableSequence, metaclass=ABCMeta):
    """Abstract Base Class for Mutable Interface.

    This class defines the interface for mutable Interface implementations.
    It inherits FrozenInterfaceABC and MutableSequence.
    """

    __slots__ = ()

    @abstractmethod
    def __add__(self, other: FrozenInterfaceABC) -> InterfaceABC:
        """Concatenate two interfaces to create a new interface.

        Add correctly updates the indices of the endpoints in the new interface.
        However, it does not change the row or class of the endpoints.

        Args
        ----
        other: Interface: The interface to concatenate with this interface.

        Returns
        -------
        Interface: A new interface containing endpoints from both interfaces.
        """
        raise NotImplementedError("InterfaceABC.__add__ must be overridden")

    @abstractmethod
    def __getitem__(self, idx: int) -> EndPointABC:  # type: ignore[override]
        """Get an endpoint by index.

        Args:
            idx: The index of the endpoint to retrieve.

        Returns:
            The EndPoint at the specified index.

        Raises:
            IndexError: If idx is out of range.
        """
        raise NotImplementedError("InterfaceABC.__getitem__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Iterator[EndPointABC]:
        """Return an iterator over the endpoints.

        Returns:
            Iterator over EndPoint objects in the interface.
        """
        raise NotImplementedError("InterfaceABC.__iter__ must be overridden")

    @abstractmethod
    def __setitem__(self, idx: int, value: FrozenEndPointABC) -> None:  # type: ignore[override]
        """Set an endpoint at a specific index.

        Args:
            idx: The index at which to set the endpoint.
            value: The endpoint to set.
        """
        raise NotImplementedError("InterfaceABC.__setitem__ must be overridden")

    @abstractmethod
    def __delitem__(self, idx: int) -> None:  # type: ignore[override]
        """Delete an endpoint at a specific index.

        Args:
            idx: The index of the endpoint to delete.
        """
        raise NotImplementedError("InterfaceABC.__delitem__ must be overridden")

    @abstractmethod
    def insert(self, index: int, value: FrozenEndPointABC) -> None:
        """Insert an endpoint at a specific index.

        Args:
            index: The index at which to insert the endpoint.
            value: The endpoint to insert.
        """
        raise NotImplementedError("InterfaceABC.insert must be overridden")

    # Abstract Modification Methods

    @abstractmethod
    def append(self, value: FrozenEndPointABC) -> None:
        """Append an endpoint to the interface.

        Args:
            value: The endpoint to append.
        """
        raise NotImplementedError("InterfaceABC.append must be overridden")

    @abstractmethod
    def clr_refs(self) -> InterfaceABC:
        """Clear all references in the interface endpoints.

        Returns:
            Self with all endpoint references cleared.
        """
        raise NotImplementedError("InterfaceABC.clr_refs must be overridden")

    @abstractmethod
    def extend(  # type: ignore[override]
        self, values: Sequence[FrozenEndPointABC] | FrozenInterfaceABC
    ) -> None:
        """Extend the interface with multiple endpoints.

        Args:
            values: The endpoints to add.

        Returns:
            Self with endpoints extended.
        """
        raise NotImplementedError("InterfaceABC.extend must be overridden")

    @abstractmethod
    def ref_shift(self, shift: int) -> InterfaceABC:
        """Shift all references in the interface endpoints by a specified amount.

        Args:
            shift: The amount to shift each reference.
        Returns:
            Self with all endpoint references shifted.
        """
        raise NotImplementedError("InterfaceABC.ref_shift must be overridden")

    @abstractmethod
    def set_cls(self, ep_cls: EPCls) -> InterfaceABC:
        """Set the class of all endpoints in the interface.

        Args:
            ep_cls: The EndPointClass to set (SRC or DST).

        Returns:
            Self with row class set.
        """
        raise NotImplementedError("InterfaceABC.set_cls must be overridden")

    @abstractmethod
    def set_refs(self, row: Row, start_ref: int = 0) -> InterfaceABC:
        """Set references for all endpoints in the interface.

        Args:
            row: The Row to set (e.g., IS, OD).
            start_ref: The starting reference number.

        Returns:
            Self with references set.
        """
        raise NotImplementedError("InterfaceABC.set_refs must be overridden")

    @abstractmethod
    def set_row(self, row: Row) -> InterfaceABC:
        """Set the row of all endpoints in the interface.

        Args:
            row: The Row to set (e.g., IS, OD).

        Returns:
            Self with row set.
        """
        raise NotImplementedError("InterfaceABC.set_row must be overridden")

    @abstractmethod
    def unconnected_eps(self) -> list[EndPointABC]:  # type: ignore[override]
        """Return a list of unconnected endpoints.

        Returns:
            List of EndPoint objects that have no connections.
        """
        raise NotImplementedError("InterfaceABC.unconnected_eps must be overridden")
