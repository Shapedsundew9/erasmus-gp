"""
Abstract Base Class for EndPoint.

This module defines the abstract interface that all EndPoint implementations
must adhere to. It establishes the contract for endpoint operations while allowing
for different concrete implementations.

The hierarchy is split into:
1. FrozenEndPointABC: Read-only interface for immutable endpoints
2. EndPointABC: Mutable interface extending FrozenEndPointABC

The abstract base class ensures consistency in the API across different endpoint types
and implementations while maintaining the flexibility to optimize specific variants.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, Sequence

from egpcommon.common_obj_abc import CommonObjABC
from egppy.genetic_code.c_graph_constants import EPCls, IfKey, Row
from egppy.genetic_code.types_def import TypesDef

# Endpoint Member Types
EndpointMemberType = tuple[Row, int, EPCls, TypesDef, list[list[str | int]]]


class FrozenEndPointABC(CommonObjABC, Hashable, metaclass=ABCMeta):
    """Abstract Base Class for Frozen (Immutable) EndPoint.

    This class defines the read-only interface for EndPoints.
    It inherits from CommonObjABC for validation methods and Hashable.

    Attributes:
        row (Row): The row identifier where this endpoint resides.
        idx (int): The index of this endpoint within its row.
        cls (EndPointClass): The endpoint class - either SRC or DST.
        typ (TypesDef): The data type associated with this endpoint.
        refs (Sequence[Sequence[str | int]]): References to connected endpoints.
    """

    __slots__ = ()

    # Abstract Attributes
    row: Row
    idx: int
    cls: EPCls
    typ: TypesDef
    refs: Sequence[Sequence[Row | int]]

    # Abstract Comparison Methods

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        """Check equality of EndPoint instances.

        Two endpoints are considered equal if all their attributes match:
        row, idx, cls, typ, and refs (including reference order).

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if the endpoints are equal, False otherwise.
        """
        raise NotImplementedError("FrozenEndPointABC.__eq__ must be overridden")

    @abstractmethod
    def __ge__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute, enabling
        natural ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx >= other.idx, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("FrozenEndPointABC.__ge__ must be overridden")

    @abstractmethod
    def __gt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute, enabling
        natural ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx > other.idx, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("FrozenEndPointABC.__gt__ must be overridden")

    @abstractmethod
    def __hash__(self) -> int:
        """Return the hash of the endpoint.

        The hash is computed from all endpoint attributes (row, idx, cls, typ, refs)
        to ensure consistent hashing for use in sets and dictionaries.

        For frozen endpoints, implementations should use a persistent hash.
        For unfrozen endpoints, implementations should calculate hash dynamically.

        Returns:
            int: Hash value for the endpoint.
        """
        raise NotImplementedError("FrozenEndPointABC.__hash__ must be overridden")

    @abstractmethod
    def __le__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute, enabling
        natural ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx <= other.idx, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("FrozenEndPointABC.__le__ must be overridden")

    @abstractmethod
    def __lt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute, enabling
        natural ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx < other.idx, False otherwise.

        Raises:
            TypeError: If other is not an EndPoint instance.
        """
        raise NotImplementedError("FrozenEndPointABC.__lt__ must be overridden")

    @abstractmethod
    def __ne__(self, value: object) -> bool:
        """Check inequality of EndPoint instances.

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if the endpoints are not equal, False otherwise.
        """
        raise NotImplementedError("FrozenEndPointABC.__ne__ must be overridden")

    # Abstract String Representation

    @abstractmethod
    def __str__(self) -> str:
        """Return the string representation of the endpoint.

        Provides a human-readable representation including all endpoint attributes
        for debugging and logging purposes.

        Returns:
            str: String representation of the endpoint showing row, idx, cls, typ, and refs.
        """
        raise NotImplementedError("FrozenEndPointABC.__str__ must be overridden")

    # Abstract Validation Methods (inherited from CommonObjABC)

    @abstractmethod
    def can_connect(self, other: FrozenEndPointABC) -> bool:
        """Check if this endpoint can connect to another endpoint.

        Connection rules:
            - Source endpoints can connect to destination endpoints.
            - Destination endpoints can connect to source endpoints.
            - Types must be compatible for connection (downcasts are not considered compatible).
            - The row connection rules must be followed.

        Args:
            other (FrozenEndPointABC): The other endpoint to check connection with.
        Returns:
            bool: True if connection is possible, False otherwise.
        """
        raise NotImplementedError("FrozenEndPointABC.can_connect must be overridden")

    @abstractmethod
    def can_downcast_connect(self, other: FrozenEndPointABC) -> bool:
        """Check if this endpoint can connect to another endpoint if it is downcast.

        Connection rules:
            - The destination endpoint is not already connected
            - It is a source-destination connection (or vice-versa)
            - Src type must be downcast-able to Dst type (upcasts & equal types return False).
            - The row connection rules must be followed.

        Args:
            other (FrozenEndPointABC): The other endpoint to check connection with.
        Returns:
            bool: True if connection is possible, False otherwise.
        """
        raise NotImplementedError("FrozenEndPointABC.can_downcast_connect must be overridden")

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the endpoint.

        Performs semantic validation that may be computationally expensive. This method
        is called automatically by verify() when CONSISTENCY logging is enabled, following
        the CommonObj validation pattern.

        Validates:
            - Reference structure and format (debug assertions)
            - All referenced endpoints would be structurally valid (does not verify existence)
            - Internal data structure integrity

        Note:
            Full bidirectional reference consistency checking (verifying that referenced
            endpoints exist and reference back correctly) requires access to other endpoints
            and is performed at the Interface or CGraph level, not here.

        Raises:
            AssertionError: If consistency checks fail (in debug mode with CONSISTENCY logging).
        """
        raise NotImplementedError("FrozenEndPointABC.consistency must be overridden")

    @abstractmethod
    def if_key(self) -> IfKey:
        """Get the IfKey corresponding to this endpoint.

        Combines the row and class of the endpoint to produce the appropriate IfKey.

        Returns:
            IfKey: The IfKey representing this endpoint's row and class.
        """
        raise NotImplementedError("FrozenEndPointABC.if_key must be overridden")

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the endpoint is connected.

        Determines whether this endpoint has any outgoing references to other endpoints.

        Returns:
            bool: True if the endpoint has at least one reference in refs, False otherwise.
        """
        raise NotImplementedError("FrozenEndPointABC.is_connected must be overridden")

    # Abstract Data Export Methods

    @abstractmethod
    def to_json(self, json_c_graph: bool = False) -> dict | list:
        """Convert the endpoint to a JSON-compatible object.

        Serializes the endpoint to a format suitable for JSON export (which requires a stable
        EndPointABC). The format varies depending on the json_c_graph parameter:

        - Standard format (json_c_graph=False): Returns a dictionary with all endpoint
          attributes (row, idx, cls, typ, refs).
        - Connection Graph format (json_c_graph=True): Returns a compact list [row, idx, typ]
          representing the connected source endpoint. Only valid for destination endpoints.

        Args:
            json_c_graph (bool): If True, returns a list suitable for JSON Connection Graph format.
                                 Only valid for destination endpoints. Defaults to False.

        Returns:
            dict | list: JSON-compatible dictionary (standard format) or list
                         (connection graph format).

        Raises:
            ValueError: If json_c_graph is True for a source endpoint.
        """
        raise NotImplementedError("FrozenEndPointABC.to_json must be overridden")

    @abstractmethod
    def verify(self) -> None:
        """Verify the integrity of the endpoint.

        Performs comprehensive validation of the endpoint structure and data, following
        the CommonObj validation pattern. This method should be called before using an
        endpoint to ensure it meets all structural and type requirements.

        Validates:
            - Index is within valid range (0-255)
            - Row and class are compatible:
                * Destination rows (I, F, W, L) must use DST class
                * Source rows (O, F, W, L) must use SRC class
            - Single-only rows (F, W, L) have index 0
            - Destination endpoints have at most 1 reference
            - All references are properly formatted as [row, idx] pairs
            - Reference row values are valid Row types
            - Reference indices are within valid range (0-255)
            - Reference row/class pairing is correct:
                * DST endpoints reference SRC rows
                * SRC endpoints reference DST rows

        Note:
            Calls consistency() automatically when CONSISTENCY logging is enabled.

        Raises:
            ValueError: If the endpoint structure is invalid.
            TypeError: If attribute types are incorrect.
        """
        raise NotImplementedError("FrozenEndPointABC.verify must be overridden")


class EndPointABC(FrozenEndPointABC, metaclass=ABCMeta):
    """Abstract Base Class for Mutable EndPoint.

    This class defines the mutable interface for EndPoints.
    It inherits from FrozenEndPointABC.

    Attributes:
        refs (list[list[str | int]]): Mutable list of references to connected endpoints.
    """

    __slots__ = ()

    # Abstract Attributes
    refs: list[list[Row | int]]  # type: ignore

    @abstractmethod
    def clr_refs(self) -> EndPointABC:
        """Clear all references in the endpoint.
        Returns:
            Self with all references cleared.
        """
        raise NotImplementedError("EndPointABC.clr_refs must be overridden")

    # Abstract Connection Methods

    @abstractmethod
    def connect(self, other: FrozenEndPointABC) -> None:
        """Connect this endpoint to another endpoint.

        Establishes a unidirectional reference from this endpoint to the other endpoint.
        For destination endpoints (DST), replaces any existing connection (single connection only).
        For source endpoints (SRC), appends to the list of connections
        (multiple connections allowed).

        Note: This method only creates a unidirectional reference. For bidirectional connections,
        this method must be called on both endpoints, or use higher-level connection methods
        provided by Interface or CGraph classes.

        Args:
            other (FrozenEndPointABC): The endpoint to connect to.
        """
        raise NotImplementedError("EndPointABC.connect must be overridden")

    @abstractmethod
    def ref_shift(self, shift: int) -> EndPointABC:
        """Shift all references in the endpoint by a given amount.
        Args:
            shift: The amount to shift each reference index by.
        Returns:
            Self with all references shifted.
        """
        raise NotImplementedError("EndPointABC.ref_shift must be overridden")

    @abstractmethod
    def set_ref(self, row: Row, idx: int, append: bool = False) -> EndPointABC:
        """Set or append to the references for an endpoint.

        This method always sets (replaces) the reference of a destination endpoint
        to the specified row and index. For a source endpoint, it appends the new reference
        to the existing list of references if append is True; otherwise, it replaces the
        entire list with the new reference.

        Args:
            row (Row): The row of the endpoint to reference.
            idx (int): The index of the endpoint to reference.
            append (bool): If True and the endpoint is a source, append the new reference;
                           otherwise, replace the references. Defaults to False.
        Returns:
            EndPointABC: Self with the reference set.
        """
        raise NotImplementedError("EndPointABC.set_ref must be overridden")
