"""Frozen Endpoint implementation for immutable graphs."""

from egpcommon.common_obj import CommonObj
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SINGLE_ONLY_ROWS,
    SOURCE_ROW_SET,
    DstIfKey,
    EPCls,
    EPClsPostfix,
    IfKey,
    Row,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.endpoint_abc import FrozenEndPointABC
from egppy.genetic_code.json_cgraph import UNKNOWN_VALID
from egppy.genetic_code.types_def import TypesDef, types_def_store


class FrozenEndPoint(CommonObj, FrozenEndPointABC):
    """Frozen End Points are immutable and introspect FrozenInterface data structures directly.

    This class provides an immutable endpoint implementation that stores references as a
    tuple instead of a list. It is memory-efficient and suitable for frozen graphs.

    Attributes:
        row (Row): The row identifier where this endpoint resides.
        idx (int): The index of this endpoint within its row (stored externally,
                   accessed via context).
        cls (EndPointClass): The endpoint class - either SRC or DST (stored as epcls).
        typ (TypesDef): The data type associated with this endpoint.
        refs_tuple (tuple[tuple[Row, int], ...]): Immutable tuple of references
                   to connected endpoints.
    """

    __slots__ = ("typ", "refs", "row", "cls", "idx", "_hash")

    def __init__(self, *args) -> None:
        """Initialize the endpoint.

        This constructor supports multiple initialization patterns:

        1. Copy from another FrozenEndPointABC instance:
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
            if isinstance(args[0], FrozenEndPointABC):
                other: FrozenEndPointABC = args[0]
                self.row = other.row
                self.idx = other.idx
                self.cls = other.cls
                self.typ = other.typ
                self.refs = tuple(tuple(ref) for ref in other.refs)
            elif isinstance(args[0], tuple) and len(args[0]) == 5:
                self.row, self.idx, self.cls, self.typ, refs_arg = args[0]
                self.refs = tuple() if refs_arg is None else tuple(tuple(ref) for ref in refs_arg)
            else:
                raise TypeError("Invalid argument for EndPoint constructor")
        elif len(args) == 4 or len(args) == 5:
            self.row: Row = args[0]
            self.idx: int = args[1]
            self.cls: EPCls = args[2]
            self.typ = args[3] if isinstance(args[3], TypesDef) else types_def_store[args[3]]
            refs_arg = args[4] if len(args) == 5 and args[4] is not None else []
            self.refs = tuple(tuple(ref) for ref in refs_arg)
        else:
            raise TypeError("Invalid arguments for EndPoint constructor")
        # Pre-compute hash for frozen endpoint
        self._hash = hash((self.row, self.idx, self.cls, self.typ, self.refs))

    def __copy__(self):
        """Called by copy.copy()"""
        return self

    def __deepcopy__(self, memo):
        """
        Called by copy.deepcopy().
        'memo' is a dictionary used to track recursion loops.
        """
        # Since we are returning self, we don't need to use memo,
        # but the signature requires it.
        return self

    def __eq__(self, value: object) -> bool:
        """Check equality of FrozenEndPoint instances.

        Two endpoints are equal if all their attributes match: row, idx, cls, typ,
        and refs (including the order and content of references).

        Args:
            value (object): Object to compare with.

        Returns:
            bool: True if all attributes are equal, False otherwise.
        """
        if not isinstance(value, FrozenEndPointABC):
            return False
        if len(self.refs) != len(value.refs):
            return False
        return (
            self.row == value.row
            and self.idx == value.idx
            and self.cls == value.cls
            and self.typ == value.typ
            and all(s[0] == v[0] and s[1] == v[1] for s, v in zip(self.refs, value.refs))
        )

    def __ge__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx >= other.idx, False otherwise.
            NotImplemented: If other is not an FrozenEndPointABC instance.
        """
        if not isinstance(other, FrozenEndPointABC):
            return NotImplemented
        return self.idx >= other.idx

    def __gt__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx > other.idx, False otherwise.
            NotImplemented: If other is not an FrozenEndPointABC instance.
        """
        if not isinstance(other, FrozenEndPointABC):
            return NotImplemented
        return self.idx > other.idx

    def __hash__(self) -> int:
        """Return the hash of the endpoint.

        Returns pre-computed hash for O(1) performance.

        Returns:
            int: Hash value computed from all endpoint attributes.
        """
        return self._hash

    def __le__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx <= other.idx, False otherwise.
            NotImplemented: If other is not an FrozenEndPointABC instance.
        """
        if not isinstance(other, FrozenEndPointABC):
            return NotImplemented
        return self.idx <= other.idx

    def __lt__(self, other: object) -> bool:
        """Compare FrozenEndPoint instances for sorting.

        Endpoints are compared based on their idx attribute for ordering within a row.

        Args:
            other (object): Object to compare with.

        Returns:
            bool: True if self.idx < other.idx, False otherwise.
            NotImplemented: If other is not an FrozenEndPointABC instance.
        """
        if not isinstance(other, FrozenEndPointABC):
            return NotImplemented
        return self.idx < other.idx

    def __ne__(self, value: object) -> bool:
        """Check inequality of FrozenEndPoint instances.

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
            str: String in format "FrozenEndPoint(row=X, idx=N, cls=CLS, typ=TYPE, refs=[...])"
        """
        return (
            f"FrozenEndPoint(row={self.row}, idx={self.idx}, cls={self.cls}"
            f", typ={self.typ}, refs={list(self.refs)})"
        )

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
        assert isinstance(other, FrozenEndPointABC), "Other endpoint is not a FrozenEndPointABC"
        # Self id the source endpoint
        if self.cls == EPCls.SRC:
            if other.cls != EPCls.DST:
                return False
            assert isinstance(self.row, SrcRow), "self.row is not a SrcRow"
            if other.row not in UNKNOWN_VALID[self.row]:
                return False
            if other.typ not in types_def_store.ancestors(self.typ):
                return False

            return True

        # Other is the source endpoint
        if other.cls != EPCls.SRC:
            return False
        assert isinstance(other.row, SrcRow), "other.row is not a SrcRow"
        if other.row not in UNKNOWN_VALID[other.row]:
            return False
        if self.typ not in types_def_store.ancestors(other.typ):
            return False
        return True

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
        assert isinstance(other, FrozenEndPointABC), "Other endpoint is not a FrozenEndPointABC"

        # Self is the source endpoint
        if self.cls == EPCls.SRC:
            # Most common reason not to connect first
            if other.is_connected():
                return False
            if other.cls != EPCls.DST:
                return False
            assert isinstance(self.row, SrcRow), "self.row is not a SrcRow"
            if other.row not in UNKNOWN_VALID[self.row]:
                return False
            if other.typ == self.typ:
                return False
            # Descendants includes self.typ, so we need to exclude that case (above)
            if other.typ not in types_def_store.descendants(self.typ):
                return False
            return True

        # Other is the source endpoint
        # Most common reason not to connect first
        if self.is_connected():
            return False
        if other.cls != EPCls.SRC:
            return False
        assert isinstance(other.row, SrcRow), "other.row is not a SrcRow"
        if other.row not in UNKNOWN_VALID[other.row]:
            return False
        if self.typ == other.typ:
            return False
        # Descendants includes other.typ, so we need to exclude that case (above)
        if self.typ not in types_def_store.descendants(other.typ):
            return False
        return True

    def consistency(self) -> None:
        """Check the consistency of the FrozenEndPoint.

        Performs semantic validation that may be expensive. This method is called
        by verify() when CONSISTENCY logging is enabled.

        Validates:
            - Reference structure matches endpoint class rules
            - Source endpoints can have multiple refs, destinations only one
            - All references point to appropriate row types
        """
        # Destination endpoints should have exactly 0 or 1 reference
        if self.cls == EPCls.DST and len(self.refs) > 1:
            raise ValueError(
                f"Destination endpoint can only have 0 or 1 reference, has {len(self.refs)}"
            )

        # Source endpoints reference destination rows, and vice versa
        if self.cls == EPCls.SRC:
            for ref in self.refs:
                if ref[0] not in DESTINATION_ROW_SET:
                    raise ValueError(
                        f"Source endpoint can only reference destination rows, got {ref[0]}"
                    )
        else:  # DST
            for ref in self.refs:
                if ref[0] not in SOURCE_ROW_SET:
                    raise ValueError(
                        f"Destination endpoint can only reference source rows, got {ref[0]}"
                    )

    def if_key(self) -> IfKey:
        """Get the IfKey corresponding to this endpoint.

        Returns:
            IfKey: The interface key for this endpoint based on its row and class.
        """
        if self.cls == EPCls.SRC:
            return SrcIfKey(f"{self.row}{EPClsPostfix.SRC}")
        return DstIfKey(f"{self.row}{EPClsPostfix.DST}")

    def is_connected(self) -> bool:
        """Check if the endpoint is connected.

        Determines whether this endpoint has any outgoing references to other endpoints.

        Returns:
            bool: True if the endpoint has at least one reference, False otherwise.
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
        if json_c_graph and self.cls == EPCls.DST:
            if len(self.refs) == 0:
                raise ValueError(
                    "Destination endpoint has no references for JSON Connection Graph format."
                )
            return [str(self.refs[0][0]), self.refs[0][1], str(self.typ)]
        if json_c_graph and self.cls == EPCls.SRC:
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
        """Verify the FrozenEndPoint object.

        Validates that the endpoint has valid structure and types.

        Raises:
            ValueError: If the endpoint is invalid.
            TypeError: If types are incorrect.
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
        if self.cls == EPCls.DST:
            self.value_error(
                self.row in DESTINATION_ROW_SET,
                f"Destination endpoint must use a destination row. "
                f"Got row={self.row} with cls=DST for endpoint {self.row}d{self.idx}. "
                f"Valid destination rows: {sorted(DESTINATION_ROW_SET)}",
            )

        # Verify row and class compatibility for source endpoints
        if self.cls == EPCls.SRC:
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
        if self.cls == EPCls.DST:
            self.value_error(
                len(self.refs) <= 1,
                f"Destination endpoint can have at most 1 reference. "
                f"Got {len(self.refs)} references for endpoint {self.row}d{self.idx}: {self.refs}",
            )

        # Verify reference structure and validity
        ref_set = set()
        is_frozen = type(self) is FrozenEndPoint  # pylint: disable=unidiomatic-typecheck
        for ref_idx, ref in enumerate(self.refs):

            # Check for duplicate references
            ref_tuple = tuple(ref)
            self.value_error(
                ref_tuple not in ref_set,
                f"Duplicate reference {ref} found at index {ref_idx} "
                f"in endpoint {self.row}{self.cls.name[0]}{self.idx}",
            )
            ref_set.add(ref_tuple)

            # Check reference is a list or a tuple as appropriate
            self.type_error(
                (isinstance(ref, list) and not is_frozen) or (isinstance(ref, tuple) and is_frozen),
                "Reference must be a list if not frozen, or a tuple if frozen"
                f", got {type(ref).__name__} at index {ref_idx} in endpoint "
                f"{self.row}{self.cls.name[0]}{self.idx}{' which is frozen.' if is_frozen else ''}",
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
            if self.cls == EPCls.DST:
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
