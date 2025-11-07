"""
Abstract Base Class for EndPoint.

This module defines the abstract interface that all EndPoint implementations
must adhere to. It establishes the contract for endpoint operations while allowing
for different concrete implementations.

The abstract base class ensures consistency in the API across different endpoint types
and implementations while maintaining the flexibility to optimize specific variants.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod

from egpcommon.common_obj_abc import CommonObjABC
from egppy.genetic_code.c_graph_constants import EndPointClass, Row
from egppy.genetic_code.types_def import TypesDef

# Endpoint Member Types
EndpointMemberType = tuple[Row, int, EndPointClass, TypesDef, list[list[str | int]]]


class EndPointABC(CommonObjABC, metaclass=ABCMeta):
    """Abstract Base Class for EndPoint.

    This class defines the essential interface that all EndPoint
    implementations must provide. It inherits from FreezableObject to support
    immutability when frozen, and CommonObjABC for validation methods.

    Endpoints represent connection points in genetic code graphs, acting as
    either sources (outputs) or destinations (inputs) with associated types
    and references to other endpoints.
    """

    __slots__ = ()

    # Abstract Attributes (must be defined in concrete implementations)
    # These are not decorated as properties since they are simple attributes.

    row: Row
    idx: int
    cls: EndPointClass
    typ: TypesDef
    refs: list[list[str | int]]

    # Abstract Comparison Methods

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        """Check equality of EndPoint instances.

        Args:
            value: Object to compare with.

        Returns:
            True if equal, False otherwise.
        """
        raise NotImplementedError("EndPointABC.__eq__ must be overridden")

    @abstractmethod
    def __ne__(self, value: object) -> bool:
        """Check inequality of EndPoint instances.

        Args:
            value: Object to compare with.

        Returns:
            True if not equal, False otherwise.
        """
        raise NotImplementedError("EndPointABC.__ne__ must be overridden")

    @abstractmethod
    def __hash__(self) -> int:
        """Return the hash of the endpoint.

        For frozen endpoints, should use a persistent hash.
        For unfrozen endpoints, should calculate dynamically.

        Returns:
            Hash value for the endpoint.
        """
        raise NotImplementedError("EndPointABC.__hash__ must be overridden")

    # Abstract Ordering Methods

    @abstractmethod
    def __lt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared on their idx.

        Args:
            other: Object to compare with.

        Returns:
            True if self < other, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("EndPointABC.__lt__ must be overridden")

    @abstractmethod
    def __le__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared on their idx.

        Args:
            other: Object to compare with.

        Returns:
            True if self <= other, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("EndPointABC.__le__ must be overridden")

    @abstractmethod
    def __gt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared on their idx.

        Args:
            other: Object to compare with.

        Returns:
            True if self > other, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("EndPointABC.__gt__ must be overridden")

    @abstractmethod
    def __ge__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared on their idx.

        Args:
            other: Object to compare with.

        Returns:
            True if self >= other, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("EndPointABC.__ge__ must be overridden")

    # Abstract String Representation

    @abstractmethod
    def __str__(self) -> str:
        """Return the string representation of the endpoint.

        Returns:
            String representation of the endpoint.
        """
        raise NotImplementedError("EndPointABC.__str__ must be overridden")

    # Abstract Connection Methods

    @abstractmethod
    def connect(self, other: EndPointABC) -> None:
        """Connect this endpoint to another endpoint.

        Args:
            other: The endpoint to connect to.

        Raises:
            RuntimeError: If this endpoint or the other endpoint is frozen.
            TypeError: If other is not an EndPoint instance.
            ValueError: If connection constraints are violated.
        """
        raise NotImplementedError("EndPointABC.connect must be overridden")

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the endpoint is connected.

        Returns:
            True if the endpoint has at least one reference, False otherwise.
        """
        raise NotImplementedError("EndPointABC.is_connected must be overridden")

    # Abstract Data Export Methods

    @abstractmethod
    def to_json(self, json_c_graph: bool = False) -> dict | list:
        """Convert the endpoint to a JSON-compatible object.

        Args:
            json_c_graph: If True, returns a list suitable for JSON Connection Graph format.
                          Only valid for destination endpoints.

        Returns:
            JSON-compatible dictionary or list representation of the endpoint.

        Raises:
            ValueError: If json_c_graph is True for a source endpoint.
        """
        raise NotImplementedError("EndPointABC.to_json must be overridden")
