"""
Mutable EndPoint Implementation.

This module provides the concrete implementation of the EndPoint abstract base class,
which represents connection points (nodes) in genetic code graphs. EndPoints act as
either sources (outputs) or destinations (inputs) with associated types and references
to other endpoints.

Key Features:
    - Mutable endpoint representation for connection graphs
    - Type-safe endpoint connections with validation
    - Support for both source and destination endpoints
    - Deep copying for mutability and independence

Classes:
    EndPoint: Concrete implementation using builtin collections
    SrcEndPoint: Convenience class for source endpoints
    DstEndPoint: Convenience class for destination endpoints

Connection Rules:
    - Source endpoints may connect to 0, 1, or multiple destination endpoints
    - Destination endpoints may only connect to a single source endpoint
    - Endpoints can only connect to endpoints of the same type
    - References must be bidirectional (facilitated by connect() method)

See Also:
    - c_graph_abc.py: Abstract base class for connection graphs (module docstring)
    - end_point_abc.py: Abstract base class definition
    - interface.py: Collection of endpoints (interfaces)
    - c_graph.py: Connection graph using interfaces
"""

from __future__ import annotations

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import CONSISTENCY, Logger, egp_logger
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SINGLE_ONLY_ROWS,
    SOURCE_ROW_SET,
    EndPointClass,
    Row,
)
from egppy.genetic_code.end_point_abc import EndPointABC
from egppy.genetic_code.types_def import TypesDef, types_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class EndPoint(CommonObj, EndPointABC):
    """Mutable Endpoint class implementation.

    This concrete implementation of EndPointABC uses builtin Python collections for
    efficient storage and manipulation of endpoint data. It provides a mutable endpoint
    representation suitable for building and modifying connection graphs.

    The EndPoint class uses __slots__ for memory efficiency and maintains endpoint state
    using standard Python lists for references, enabling dynamic modification of connections
    during graph construction.

    Attributes:
        row (Row): The row identifier where this endpoint resides.
        idx (int): The index of this endpoint within its row (0-255).
        cls (EndPointClass): The endpoint class - either SRC (source) or DST (destination).
        typ (TypesDef): The data type associated with this endpoint.
        refs (list[list[str | int]]): Mutable list of references to connected endpoints.

    See Also:
        - EndPointABC: Abstract base class defining the endpoint interface
        - SrcEndPoint: Convenience class for creating source endpoints
        - DstEndPoint: Convenience class for creating destination endpoints
        - Interface: Collection of endpoints forming an interface
        - CGraph: Connection graph composed of interfaces
    """

    __slots__ = ("row", "idx", "cls", "typ", "refs")

    def __init__(self, *args) -> None:
        """Initialize the endpoint.

        This constructor supports multiple initialization patterns:

        1. Copy from another EndPointABC instance:
           EndPoint(other_endpoint)

        2. Initialize from a 5-tuple:
           EndPoint((row, idx, cls, typ, refs))

        3. Initialize from explicit arguments (4 or 5 args):
           EndPoint(row, idx, cls, typ)
           EndPoint(row, idx, cls, typ, refs)

        The typ argument can be either a TypesDef instance or a string key that
        will be looked up in types_def_store. The refs argument, if provided,
        will be deep copied to ensure mutability and independence.

        Args:
            *args: Variable arguments supporting the patterns described above.

        Raises:
            TypeError: If arguments don't match any supported initialization pattern.
        """
        super().__init__()
        if len(args) == 1:
            if isinstance(args[0], EndPointABC):
                other: EndPointABC = args[0]
                self.row = other.row
                self.idx = other.idx
                self.cls = other.cls
                self.typ = other.typ
                self.refs = [list(ref) for ref in other.refs]
            elif isinstance(args[0], tuple) and len(args[0]) == 5:
                self.row, self.idx, self.cls, self.typ, refs_arg = args[0]
                self.refs = [] if refs_arg is None else [list(ref) for ref in refs_arg]
            else:
                raise TypeError("Invalid argument for EndPoint constructor")
        elif len(args) == 4 or len(args) == 5:
            self.row: Row = args[0]
            self.idx: int = args[1]
            self.cls: EndPointClass = args[2]
            self.typ = args[3] if isinstance(args[3], TypesDef) else types_def_store[args[3]]
            refs_arg = args[4] if len(args) == 5 and args[4] is not None else []
            self.refs = [list(ref) for ref in refs_arg]
        else:
            raise TypeError("Invalid arguments for EndPoint constructor")

    def __eq__(self, value: object) -> bool:
        """Check equality of EndPoint instances.

        Two endpoints are equal if all their attributes match: row, idx, cls, typ,
        and refs (including the order and content of references).

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if all attributes are equal, False otherwise.
        """
        if not isinstance(value, EndPointABC):
            return False
        if len(self.refs) != len(value.refs):
            return False
        return (
            self.row == value.row
            and self.idx == value.idx
            and self.cls == value.cls
            and self.typ == value.typ
            and all(a == b for a, b in zip(self.refs, value.refs))
        )

    def __ge__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx >= other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx >= other.idx

    def __gt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx > other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx > other.idx

    def __hash__(self) -> int:
        """Return the hash of the endpoint.

        Computes a hash from all endpoint attributes (row, idx, cls, typ, refs)
        to enable use in sets and as dictionary keys. References are converted
        to tuples for hashability.

        Returns:
            int: Hash value computed from all endpoint attributes.
        """
        tuple_refs = tuple(tuple(ref) for ref in self.refs)
        return hash((self.row, self.idx, self.cls, self.typ, tuple_refs))

    def __le__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx <= other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx <= other.idx

    def __lt__(self, other: object) -> bool:
        """Compare EndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx < other.idx, False otherwise.
            NotImplemented: If other is not an EndPointABC instance.
        """
        if not isinstance(other, EndPointABC):
            return NotImplemented
        return self.idx < other.idx

    def __ne__(self, value: object) -> bool:
        """Check inequality of EndPoint instances.

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if endpoints are not equal, False otherwise.
        """
        return not self.__eq__(value)

    def __str__(self) -> str:
        """Return the string representation of the endpoint.

        Provides a detailed string showing all endpoint attributes for debugging
        and logging purposes.

        Returns:
            str: String in format "EndPoint(row=X, idx=N, cls=CLS, typ=TYPE, refs=[...])"
        """
        return (
            f"EndPoint(row={self.row}, idx={self.idx}, cls={self.cls}"
            f", typ={self.typ}, refs=[{self.refs}])"
        )

    def connect(self, other: EndPointABC) -> None:
        """Connect this endpoint to another endpoint.

        Establishes a unidirectional reference from this endpoint to the other endpoint.
        The behavior differs based on endpoint class:

        - Destination endpoints (DST): Replaces refs with a single reference to other.
        - Source endpoints (SRC): Appends a reference to other to the refs list.

        Note: This creates only a unidirectional connection. For bidirectional connections,
        call connect() on both endpoints or use higher-level methods in Interface/CGraph.

        Args:
            other (EndPointABC): The endpoint to connect to.
        """
        assert isinstance(other, EndPointABC), "Can only connect to another EndPoint instance"
        if self.cls == EndPointClass.DST:
            self.refs = [[other.row, other.idx]]
        else:
            self.refs.append([other.row, other.idx])

    def is_connected(self) -> bool:
        """Check if the endpoint is connected.

        Returns:
            bool: True if refs contains at least one reference, False otherwise.
        """
        return len(self.refs) > 0

    def to_json(self, json_c_graph: bool = False) -> dict | list:
        """Convert the endpoint to a JSON-compatible object.

        Supports two output formats:

        1. Standard format (json_c_graph=False):
           Returns a dictionary with all endpoint attributes:
           {"row": "X", "idx": N, "cls": "DST"|"SRC", "typ": "type_str", "refs": [[...], ...]}

        2. Connection Graph format (json_c_graph=True):
           Returns a compact list representing the connected source endpoint: [row, idx, type_str]
           Only valid for destination endpoints.

        Args:
            json_c_graph (bool): If True, returns connection graph format. Defaults to False.

        Returns:
            dict | list: Dictionary (standard format) or list (connection graph format).

        Raises:
            ValueError: If json_c_graph is True for a source endpoint.
        """
        if json_c_graph and self.cls == EndPointClass.DST:
            if len(self.refs) == 0:
                raise ValueError(
                    "Destination endpoint has no references for JSON Connection Graph format."
                )
            return [self.refs[0][0], self.refs[0][1], str(self.typ)]
        if json_c_graph and self.cls == EndPointClass.SRC:
            raise ValueError(
                "Source endpoints cannot be converted to JSON Connection Graph format."
            )
        return {
            "row": str(self.row),
            "idx": self.idx,
            "cls": self.cls,
            "typ": str(self.typ),
            "refs": [list(ref) for ref in self.refs],
        }

    def verify(self) -> None:
        """Verify the integrity of the endpoint.

        Validates that the endpoint has valid structure including:
        - Index is within valid range (0-255)
        - Row and class are compatible (destination rows with DST class, source rows with SRC class)
        - Single-only rows (F, W, L) have index 0
        - Destination endpoints have at most 1 reference
        - All references are properly formatted and valid

        Raises:
            ValueError: If the endpoint is invalid.
        """
        # Verify index range
        self.value_error(
            0 <= self.idx < 256,
            f"Endpoint index must be between 0 and 255, got {self.idx} "
            f"for endpoint {self.row}{self.cls.name[0]}{self.idx}",
        )

        # Verify that row is not U (special case)
        self.value_error(
            self.row != "U",
            f"Endpoint row cannot be 'U', got {self.row} "
            f"for endpoint {self.row}{self.cls.name[0]}{self.idx}",
        )

        # Verify that typ is a TypesDef instance
        self.type_error(
            isinstance(self.typ, TypesDef),
            f"Endpoint type must be a TypesDef instance, got {type(self.typ).__name__} "
            f"for endpoint {self.row}{self.cls.name[0]}{self.idx}",
        )

        # Verify row and class compatibility for destination endpoints
        if self.cls == EndPointClass.DST:
            self.value_error(
                self.row in DESTINATION_ROW_SET,
                f"Destination endpoint must use a destination row. "
                f"Got row={self.row} with cls=DST for endpoint {self.row}d{self.idx}. "
                f"Valid destination rows: {sorted(DESTINATION_ROW_SET)}",
            )

        # Verify row and class compatibility for source endpoints
        if self.cls == EndPointClass.SRC:
            self.value_error(
                self.row in SOURCE_ROW_SET,
                f"Source endpoint must use a source row. "
                f"Got row={self.row} with cls=SRC for endpoint {self.row}s{self.idx}. "
                f"Valid source rows: {sorted(SOURCE_ROW_SET)}",
            )

        # Verify single-only row constraint (F, W, L rows can only have index 0)
        if self.row in SINGLE_ONLY_ROWS:
            self.value_error(
                self.idx == 0,
                f"Row {self.row} can only have a single endpoint (index 0). "
                f"Got index {self.idx} for endpoint {self.row}{self.cls.name[0]}{self.idx}",
            )

        # Verify destination endpoints have at most one reference
        if self.cls == EndPointClass.DST:
            self.value_error(
                len(self.refs) <= 1,
                f"Destination endpoint can have at most 1 reference. "
                f"Got {len(self.refs)} references for endpoint {self.row}d{self.idx}: {self.refs}",
            )

        # Verify reference structure and validity
        ref_set = set()
        for ref_idx, ref in enumerate(self.refs):

            # Check for duplicate references
            ref_tuple = tuple(ref)
            self.value_error(
                ref_tuple not in ref_set,
                f"Duplicate reference {ref} found at index {ref_idx} "
                f"in endpoint {self.row}{self.cls.name[0]}{self.idx}",
            )
            ref_set.add(ref_tuple)

            # Check reference is a list
            self.type_error(
                isinstance(ref, list),
                f"Reference must be a list, got {type(ref).__name__} "
                f"at index {ref_idx} in endpoint {self.row}{self.cls.name[0]}{self.idx}",
            )

            # Check reference has exactly 2 elements [row, idx]
            self.value_error(
                len(ref) == 2,
                f"Reference must have exactly 2 elements [row, idx], got {len(ref)} elements "
                f"at index {ref_idx} in endpoint {self.row}{self.cls.name[0]}{self.idx}: {ref}",
            )

            # Extract and validate reference components
            ref_row = ref[0]
            ref_ep_idx = ref[1]

            # Check reference row is valid
            self.type_error(
                isinstance(ref_row, str),
                f"Reference row must be a string, got {type(ref_row).__name__} "
                f"at index {ref_idx} in endpoint {self.row}{self.cls.name[0]}{self.idx}: {ref}",
            )

            # Verify reference row is in valid ROW_SET
            self.value_error(
                ref_row in ROW_SET,
                f"Reference row must be a valid row. "
                f"Got '{ref_row}' at index {ref_idx} in endpoint"
                f"{self.row}{self.cls.name[0]}{self.idx}. "
                f"Valid rows: {ROW_SET}",
            )

            # Check reference index is valid
            self.type_error(
                isinstance(ref_ep_idx, int),
                f"Reference index must be an integer, got {type(ref_ep_idx).__name__} "
                f"at index {ref_idx} in endpoint {self.row}{self.cls.name[0]}{self.idx}: {ref}",
            )

            # Verify reference index is within valid range (0-255)
            assert isinstance(ref_ep_idx, int), "Reference index must be an integer"
            self.value_error(
                0 <= ref_ep_idx < 256,
                f"Reference index must be between 0 and 255, got {ref_ep_idx}",
            )

            # Verify row/class pairing: DST endpoints should reference SRC rows, and vice versa
            if self.cls == EndPointClass.DST:
                self.value_error(
                    ref_row in SOURCE_ROW_SET,
                    f"Destination endpoint must reference a source row. "
                    f"Got reference to row '{ref_row}' at index {ref_idx} "
                    f"in endpoint {self.row}d{self.idx}. "
                    f"Valid source rows: {sorted(SOURCE_ROW_SET)}",
                )
            else:  # self.cls == EndPointClass.SRC
                self.value_error(
                    ref_row in DESTINATION_ROW_SET,
                    f"Source endpoint must reference a destination row. "
                    f"Got reference to row '{ref_row}' at index {ref_idx} "
                    f"in endpoint {self.row}s{self.idx}. "
                    f"Valid destination rows: {sorted(DESTINATION_ROW_SET)}",
                )

        # Call parent verify() which will trigger consistency() if CONSISTENCY logging is enabled
        super().verify()

    def consistency(self) -> None:
        """Check the consistency of the endpoint.

        Performs semantic validation that may be expensive. This method is called
        by verify() when CONSISTENCY logging is enabled.

        Validates:
        - Reference structure and format (debug assertions)
        - All referenced endpoints would be valid (structural check only)

        Note: Full bidirectional reference consistency checking requires access
        to other endpoints and is performed at the Interface or CGraph level.
        """
        if _logger.isEnabledFor(level=CONSISTENCY):
            _logger.log(
                level=CONSISTENCY,
                msg=f"Consistency check for EndPoint {self.row}{self.cls.name[0]}{self.idx}",
            )

            # Additional debug assertions for reference validation
            for ref in self.refs:
                assert isinstance(ref, list), f"Reference must be a list, got {type(ref)}"
                assert len(ref) == 2, f"Reference must have 2 elements, got {len(ref)}"
                assert isinstance(ref[0], str), f"Row must be a string, got {type(ref[0])}"
                assert ref[0] in ROW_SET, f"Row must be in ROW_SET, got {ref[0]}"
                assert isinstance(ref[1], int), f"Index must be an int, got {type(ref[1])}"
                assert 0 <= ref[1] <= 255, f"Index must be 0-255, got {ref[1]}"

        # Call parent consistency()
        super().consistency()


class SrcEndPoint(EndPoint):
    """Source Endpoint convenience class.

    A convenience class for creating source (SRC) endpoints with simplified initialization.
    Automatically sets the endpoint class to SRC, reducing boilerplate when creating
    output endpoints.

    Args:
        row (Row): The row identifier.
        idx (int): The endpoint index within the row.
        typ (TypesDef | str): The endpoint type.
        refs (list[list[str | int]] | None): Optional initial references. Defaults to None.

    Example:
        src_ep = SrcEndPoint('O', 0, 'int')
        src_ep = SrcEndPoint('O', 1, types_def_store['float'], [[I', 0]])
    """

    def __init__(self, *args) -> None:
        """Initialize the source endpoint.

        Args:
            *args: (row, idx, typ) or (row, idx, typ, refs)
        """
        super().__init__(
            args[0], args[1], EndPointClass.SRC, args[2], args[3] if len(args) == 4 else None
        )


class DstEndPoint(EndPoint):
    """Destination Endpoint convenience class.

    A convenience class for creating destination (DST) endpoints with simplified initialization.
    Automatically sets the endpoint class to DST, reducing boilerplate when creating
    input endpoints.

    Args:
        row (Row): The row identifier.
        idx (int): The endpoint index within the row.
        typ (TypesDef | str): The endpoint type.
        refs (list[list[str | int]] | None): Optional initial references. Defaults to None.

    Example:
        dst_ep = DstEndPoint('I', 0, 'int')
        dst_ep = DstEndPoint('I', 1, types_def_store['float'], [['O', 0]])
    """

    def __init__(self, *args) -> None:
        """Initialize the destination endpoint.

        Args:
            *args: (row, idx, typ) or (row, idx, typ, refs)
        """
        super().__init__(
            args[0], args[1], EndPointClass.DST, args[2], args[3] if len(args) == 4 else None
        )
