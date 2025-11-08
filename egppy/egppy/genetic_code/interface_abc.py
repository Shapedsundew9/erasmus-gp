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
from collections.abc import Iterator

from egpcommon.common_obj_abc import CommonObjABC
from egppy.genetic_code.c_graph_constants import EndPointClass
from egppy.genetic_code.endpoint_abc import EndPointABC


class InterfaceABC(CommonObjABC, metaclass=ABCMeta):
    """Abstract Base Class for Interface.

    This class defines the essential interface that all Interface
    implementations must provide. It inherits CommonObjABC for validation methods.

    Interfaces define collections of endpoints that represent connections in
    genetic code, either as sources (inputs) or destinations (outputs).
    """

    __slots__ = ()

    # Abstract Container Protocol Methods

    @abstractmethod
    def __getitem__(self, idx: int) -> EndPointABC:
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
    def __len__(self) -> int:
        """Return the number of endpoints in the interface.

        Returns:
            Number of endpoints in this interface.
        """
        raise NotImplementedError("InterfaceABC.__len__ must be overridden")

    @abstractmethod
    def __setitem__(self, idx: int, value: EndPointABC) -> None:
        """Set an endpoint at a specific index.

        Args:
            idx: The index at which to set the endpoint.
            value: The endpoint to set.
        """
        raise NotImplementedError("InterfaceABC.__setitem__ must be overridden")

    # Abstract Comparison Methods

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        """Check equality of Interface instances.

        Args:
            value: Object to compare with.

        Returns:
            True if equal, False otherwise.
        """
        raise NotImplementedError("InterfaceABC.__eq__ must be overridden")

    @abstractmethod
    def __hash__(self) -> int:
        """Return the hash of the interface.

        Returns:
            Hash value for the interface.
        """
        raise NotImplementedError("InterfaceABC.__hash__ must be overridden")

    # Abstract String Representation

    @abstractmethod
    def __str__(self) -> str:
        """Return the string representation of the interface.

        Returns:
            String representation of the interface.
        """
        raise NotImplementedError("InterfaceABC.__str__ must be overridden")

    # Abstract Arithmetic Operations

    @abstractmethod
    def __add__(self, other: InterfaceABC) -> InterfaceABC:
        """Concatenate two interfaces to create a new interface.

        Args:
            other: The interface to concatenate with this interface.

        Returns:
            A new interface containing endpoints from both interfaces.
        """
        raise NotImplementedError("InterfaceABC.__add__ must be overridden")

    # Abstract Modification Methods

    @abstractmethod
    def append(self, value: EndPointABC) -> None:
        """Append an endpoint to the interface.

        Args:
            value: The endpoint to append.
        """
        raise NotImplementedError("InterfaceABC.append must be overridden")

    @abstractmethod
    def extend(self, values: list[EndPointABC] | tuple[EndPointABC, ...] | InterfaceABC) -> None:
        """Extend the interface with multiple endpoints.

        Args:
            values: The endpoints to add.
        """
        raise NotImplementedError("InterfaceABC.extend must be overridden")

    # Abstract Property Methods

    @abstractmethod
    def cls(self) -> EndPointClass:
        """Return the class of the interface.

        Returns:
            The EndPointClass (SRC or DST) of this interface.
        """
        raise NotImplementedError("InterfaceABC.cls must be overridden")

    # Abstract Data Export Methods

    @abstractmethod
    def to_json(self, json_c_graph: bool = False) -> list:
        """Convert the interface to a JSON-compatible object.

        Args:
            json_c_graph: If True, returns a list suitable for JSON Connection Graph format.

        Returns:
            List of JSON-compatible endpoint representations.
        """
        raise NotImplementedError("InterfaceABC.to_json must be overridden")

    @abstractmethod
    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints).

        Returns:
            List of TypesDef UIDs for each endpoint.
        """
        raise NotImplementedError("InterfaceABC.to_td_uids must be overridden")

    @abstractmethod
    def types(self) -> tuple[list[int], bytes]:
        """Return a tuple of the ordered type UIDs and the indices into it.

        Returns:
            Tuple of (ordered_type_uids, byte_indices).
        """
        raise NotImplementedError("InterfaceABC.types must be overridden")

    @abstractmethod
    def ordered_td_uids(self) -> list[int]:
        """Return the ordered type definition UIDs.

        Returns:
            Sorted list of unique TypesDef UIDs.
        """
        raise NotImplementedError("InterfaceABC.ordered_td_uids must be overridden")

    @abstractmethod
    def unconnected_eps(self) -> list[EndPointABC]:
        """Return a list of unconnected endpoints.

        Returns:
            List of EndPoint objects that have no connections.
        """
        raise NotImplementedError("InterfaceABC.unconnected_eps must be overridden")
