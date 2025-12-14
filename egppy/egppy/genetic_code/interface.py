"""The Interface Module."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Sequence

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import CONSISTENCY, Logger, egp_logger
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SOURCE_ROW_SET,
    DstRow,
    EPCls,
    Row,
    SrcRow,
)
from egppy.genetic_code.endpoint import EndPoint, TypesDef
from egppy.genetic_code.endpoint_abc import EndPointABC, EndpointMemberType, FrozenEndPointABC
from egppy.genetic_code.frozen_interface import FrozenInterface
from egppy.genetic_code.interface_abc import MAX_EPS, FrozenInterfaceABC, InterfaceABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def unpack_dst_ref(ref: list[int | Row] | tuple[Row, int]) -> tuple[DstRow, int]:
    """Unpack a destination reference into its components.

    Args
    ----
    ref: A reference to unpack, either as a list or tuple.

    Returns
    -------
    A tuple containing the destination row and index.
    """
    row, idx = unpack_ref(ref)
    assert row in DESTINATION_ROW_SET, f"Row must be in DESTINATION_ROW_SET, got {row}"
    return DstRow(row), idx


def unpack_ref(ref: list[int | Row] | tuple[Row, int]) -> tuple[Row, int]:
    """Unpack a reference into its components.

    Args
    ----
    ref: A reference to unpack, either as a list or tuple.

    Returns
    -------
    A tuple containing the row and index.
    """
    row = ref[0]
    idx = ref[1]
    assert isinstance(row, str), "Row must be a Row"
    assert row in ROW_SET, f"Row must be in ROW_SET, got {row}"
    assert isinstance(idx, int), "Index must be an int"
    assert 0 <= idx <= 255, "Index must be between 0 and 255"
    return row, idx


def unpack_src_ref(ref: list[int | Row] | tuple[Row, int]) -> tuple[SrcRow, int]:
    """Unpack a source reference into its components.

    Args
    ----
    ref: A reference to unpack, either as a list or tuple.

    Returns
    -------
    A tuple containing the source row and index.
    """
    row, idx = unpack_ref(ref)
    assert row in SOURCE_ROW_SET, f"Row must be in SOURCE_ROW_SET, got {row}"
    return SrcRow(row), idx


class Interface(CommonObj, FrozenInterface, InterfaceABC):
    """The Interface class provides a base for defining interfaces in the EGP system."""

    __slots__ = ("endpoints", "_hash", "_row", "_cls")

    def __init__(  # pylint: disable=super-init-not-called
        self,
        endpoints: (
            Sequence[EndPoint]
            | Sequence[EndpointMemberType]
            | Sequence[list | tuple]
            | Sequence[str | int | TypesDef]
            | FrozenInterfaceABC
        ),
        row: Row,
        rrow: Row | None = None,
        rsidx: int = 0,
    ) -> None:
        """Initialize the Interface class.

        Args
        ----
        endpoints: Sequence[...]: A sequence of EndPoint objects or
            sequences that define the interface. If a sequence of sequences is provided, each
            inner sequence should contain [ref_row, ref_idx, typ] and the row parameter must
            be != None. If a sequence of (mixed) strings, integers or TypesDef is provided,
            they will be treated as EGP types, in order, as destinations on the row specified unless
            the row can only be a source.
            Any objects will be deep-copied to ensure mutability & independence.
        row: Row: The row of the interface. The correct row enum must be used (DstRow or SrcRow).
        rrow: Row | None: The row to use for references. When endpoints are not EndPoints
            None indicates no references i.e. an empty list. If provided, this will override
            any ref row specified in the endpoint sequences.
        rsidx: int: The starting index to use for references when rrow is provided.
        """
        CommonObj.__init__(self)
        self.endpoints: list[EndPoint] = []
        self._hash: int = 0
        self._row = row
        self._cls = EPCls.DST if isinstance(row, DstRow) else EPCls.SRC

        # Assert valid row if provided
        assert isinstance(row, (DstRow, SrcRow, type(None))), "Row must be DstRow, SrcRow or None"

        # Nothing to do if there are no endpoints
        if len(endpoints) == 0:
            return

        # Handle case where endpoints is an FrozenInterfaceABC or contains EndPointABC instances
        if isinstance(endpoints, FrozenInterfaceABC) or isinstance(endpoints[0], EndPointABC):
            assert all(
                isinstance(ep, FrozenEndPointABC) for ep in endpoints
            ), "All endpoints must be FrozenEndPointABC instances"
            self.endpoints = [
                EndPoint(
                    self._row,
                    idx,
                    self._cls,
                    ep.typ,  # type: ignore
                    ep.refs if rrow is None else [[rrow, rsidx + idx]],  # type: ignore
                )
                for idx, ep in enumerate(endpoints)
            ]
            return

        # Handle case where endpoints are JSONCGraph-style sequences
        if isinstance(endpoints[0], (list, tuple)) and len(endpoints[0]) == 3:
            self.endpoints = [
                EndPoint(
                    self._row,
                    idx,
                    self._cls,
                    ep[2],  # type: ignore
                    [ep[0:2]] if rrow is None else [[rrow, rsidx + idx]],  # type: ignore
                )
                for idx, ep in enumerate(endpoints)
            ]
            return

        # Handle the type sequence case
        if isinstance(endpoints[0], (str, int, TypesDef)):
            self.endpoints = [
                EndPoint(
                    self._row,
                    idx,
                    self._cls,
                    ep,  # type: ignore
                    [] if rrow is None else [[rrow, rsidx + idx]],  # type: ignore
                )
                for idx, ep in enumerate(endpoints)
            ]
            return

        # Handle mixed endpoint member types
        if isinstance(endpoints[0], tuple) and len(endpoints[0]) == 5:
            self.endpoints = [
                EndPoint(
                    self._row,
                    idx,
                    self._cls,
                    ep[3],  # type: ignore
                    ep[4] if rrow is None else [[rrow, rsidx + idx]],  # type: ignore
                )
                for idx, ep in enumerate(endpoints)
            ]
            return

        # If we get here, we have an unsupported type
        raise TypeError(
            f"Unsupported endpoints type: {type(endpoints)} with first"
            f" element type {type(endpoints[0])}. "
            "Supported types are: FrozenInterfaceABC, sequence of EndPointABC, "
            "sequence of 3-element tuples (e.g. ['row', idx, type]), "
            "sequence of types (e.g. [TypesDef, ...]), or sequence of 5-element"
            " tuples (e.g. [row, idx, cls, type, refs]). "
            "Example of valid input: [('dst', 0, EPCls.DST, TypesDef, [[...]]), ...]"
        )

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
        if not isinstance(other, FrozenInterfaceABC):
            raise TypeError(f"Can only add FrozenInterfaceABC to InterfaceABC, got {type(other)}")

        # Handle empty interfaces
        if len(self.endpoints) == 0:
            return Interface(other, self._row)
        if len(other) == 0:
            return Interface(self, self._row)

        # Create new interface with copied endpoints from both
        # Create copies of endpoints with updated indices (with clean references)
        niface = Interface(self, self._row)
        niface.extend(other)
        return niface

    def __delitem__(self, idx: int) -> None:
        """Delete an endpoint at a specific index.

        Args:
            idx: The index of the endpoint to delete.
        """
        del self.endpoints[idx]
        # Update indices of subsequent endpoints
        for i in range(idx, len(self.endpoints)):
            self.endpoints[i].idx = i

    def __eq__(self, value: object) -> bool:
        """Check equality of Interface instances.
        This implements deep equality checking between two Interface instances
        which can be quite expensive for large interfaces.
        """
        if not isinstance(value, FrozenInterfaceABC):
            return False
        if len(self) != len(value):
            return False
        return all(a == b for a, b in zip(self, value))

    def __getitem__(self, idx: int) -> EndPointABC:
        """Get an endpoint by index."""
        return self.endpoints[idx]

    def __hash__(self) -> int:
        """Return the hash of the interface."""
        return hash(tuple(hash(ep) for ep in self.endpoints))

    def __iter__(self) -> Iterator[EndPointABC]:
        """Return an iterator over the endpoints."""
        return iter(self.endpoints)

    def __len__(self) -> int:
        """Return the number of endpoints in the interface."""
        return len(self.endpoints)

    def __setitem__(self, idx: int, value: FrozenEndPointABC) -> None:
        """Set an endpoint at a specific index.

        Args
        ----
        idx: int: The index at which to set the endpoint.
        value: EndPoint: The endpoint to set.

        Raises
        ------
        RuntimeError: If the interface is frozen.
        TypeError: If value is not an EndPointABC instance.
        IndexError: If idx is out of range.
        ValueError: If the endpoint's row or class doesn't match existing endpoints.
        """
        if not isinstance(value, FrozenEndPointABC):
            raise TypeError(f"Expected EndPointABC, got {type(value)}")
        if idx < 0 or idx >= len(self.endpoints):
            raise IndexError(
                f"Index {idx} out of range for interface with {len(self.endpoints)} endpoints"
            )
        _value = EndPoint(value)  # Make a copy to ensure mutability & independence
        _value.idx = idx  # Ensure the index is correct
        self.endpoints[idx] = _value

    def __str__(self) -> str:
        """Return the string representation of the interface."""
        return f"Interface({', '.join(str(ep.typ) for ep in self.endpoints)})"

    def append(self, value: FrozenEndPointABC) -> None:
        """Append an endpoint to the interface.

        Append correctly sets the index of the appended endpoint.
        However, it does not change the row or class of the endpoint.

        Args
        ----
        value: EndPointABC: The endpoint to append.
        """
        _value = EndPoint(value)  # Make a copy to ensure mutability & independence
        _value.idx = len(self.endpoints)  # Ensure the index is correct
        _value.cls = self._cls  # Ensure the class matches
        if _value.idx >= MAX_EPS:
            raise ValueError(f"Cannot append endpoint to interface beyond {MAX_EPS} endpoints")
        self.endpoints.append(_value)

    def clr_refs(self) -> InterfaceABC:
        """Clear all references in the interface endpoints.
        Returns:
            Interface: Self with all endpoint references cleared."""
        for ep in self.endpoints:
            ep.clr_refs()
        return self

    def consistency(self) -> None:
        """Check the consistency of the Interface.

        Performs semantic validation that may be expensive. This method is called
        by verify() when CONSISTENCY logging is enabled.
        """
        _logger.log(
            level=CONSISTENCY,
            msg=f"Consistency check for Interface with {len(self.endpoints)} endpoints",
        )

        # Call parent consistency()
        super().consistency()

    def extend(self, values: Sequence[FrozenEndPointABC] | FrozenInterfaceABC) -> None:
        """Extend the interface with multiple endpoints.

        Extend correctly sets the indices of the appended endpoints.
        However, it does not change the row, class or refs of the endpoint.

        Args
        ----
        values: list[EndPoint] | tuple[EndPoint, ...]: The endpoints to add.
        """
        if len(self) + len(values) > MAX_EPS:
            raise ValueError(
                f"Cannot extend interface beyond {MAX_EPS} endpoints "
                f"(current: {len(self)}, adding: {len(values)})"
            )
        for idx, value in enumerate(values, start=len(self.endpoints)):
            _value = EndPoint(value)  # Make a copy to ensure mutability & independence
            _value.idx = idx  # Ensure the index is correct
            _value.cls = self._cls  # Ensure the class matches
            self.endpoints.append(_value)

    def insert(self, index: int, value: FrozenEndPointABC) -> None:
        """Insert an endpoint at a specific index.

        Args:
            index: The index at which to insert the endpoint.
            value: The endpoint to insert.
        """
        _value = EndPoint(value)
        _value.cls = self._cls  # Ensure the class matches
        _value.row = self._row  # Ensure the row matches
        self.endpoints.insert(index, _value)
        # Update indices of subsequent endpoints
        for i in range(index, len(self.endpoints)):
            self.endpoints[i].idx = i

    def ref_shift(self, shift: int) -> InterfaceABC:
        """Shift all references in the interface endpoints by a specified amount.

        Args:
            shift: The amount to shift each reference index by.
        Returns:
            Interface: Self with all endpoint references shifted.
        """
        for ep in self.endpoints:
            ep.ref_shift(shift)
        return self

    def set_cls(self, ep_cls) -> InterfaceABC:
        """Set the class of all endpoints in the interface."""
        self._cls = ep_cls
        for ep in self.endpoints:
            ep.cls = ep_cls
        return self

    def set_refs(self, row: Row, start_ref: int = 0) -> InterfaceABC:
        """Set (replace) all references in the interface endpoints.

        Args
        ----
        row: Row: The row to set for all references.
        start_ref: int: The starting reference index.

        Returns
        -------
        Interface: Self with all endpoint references set.
        """
        for idx, ep in enumerate(self.endpoints):
            ep.set_ref(row, start_ref + idx)
        return self

    def set_row(self, row: Row) -> InterfaceABC:
        """Set the row of all endpoints in the interface.

        Args
        ----
        row: Row: The row to set for all endpoints.

        Returns
        -------
        Interface: Self with row set.
        """
        self._row = row
        for ep in self.endpoints:
            ep.row = row
        return self

    def sorted_unique_td_uids(self) -> list[int]:
        """Return the ordered type definition UIDs."""
        return sorted(set(ep.typ.uid for ep in self.endpoints))

    def to_json(self, json_c_graph: bool = False) -> list:
        """Convert the interface to a JSON-compatible object.
        If `json_c_graph` is True, it returns a list suitable for JSON Connection Graph format.
        """
        return [ep.to_json(json_c_graph=json_c_graph) for ep in self.endpoints]

    def to_td(self) -> tuple[TypesDef, ...]:
        """Convert the interface to a tuple of TypesDef objects."""
        return tuple(ep.typ for ep in self.endpoints)

    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints)."""
        return [ep.typ.uid for ep in self.endpoints]

    def types_and_indices(self) -> tuple[list[int], bytes]:
        """Return a tuple of the ordered type UIDs and the indices into to it."""
        otu: list[int] = self.sorted_unique_td_uids()
        lookup_indices: dict[int, int] = {uid: idx for idx, uid in enumerate(otu)}
        indices = bytes(lookup_indices[ep.typ.uid] for ep in self.endpoints)
        return otu, indices

    def unconnected_eps(self) -> list[EndPointABC]:  # type: ignore[override]
        """Return a list of unconnected endpoints."""
        return [ep for ep in self.endpoints if not ep.is_connected()]

    def verify(self) -> None:
        """Verify the Interface object.

        Validates that the interface has valid structure and all endpoints are consistent.
        Empty interfaces (like NULL_INTERFACE) are allowed as sentinel values.

        Raises
        ------
        ValueError: If the interface is invalid.
        """
        # Allow empty interfaces (e.g., NULL_INTERFACE) as sentinel values
        if len(self.endpoints) == 0:
            super().verify()
            return

        # Check all endpoints are EndPoint instances
        if not all(isinstance(ep, EndPoint) for ep in self.endpoints):
            raise ValueError("All endpoints must be EndPoint instances.")

        # Check all endpoints have the same row
        if not all(ep.row == self._row for ep in self.endpoints):
            raise ValueError(f"All endpoints must have the same row. Expected {self._row}.")

        # Check all endpoints have the same class
        if not all(ep.cls == self._cls for ep in self.endpoints):
            raise ValueError(f"All endpoints must have the same class. Expected {self._cls}.")

        # Verify each endpoint
        for ep in self.endpoints:
            ep.verify()

        # Call parent verify() which will trigger consistency() if CONSISTENCY logging is enabled
        super().verify()


# Re-use the Interface object deduplicator for both SrcInterface and DstInterface
class SrcInterface(Interface):
    """Source Interface class."""

    def __init__(
        self,
        endpoints: Sequence[EndPoint] | Sequence[list | tuple] | Sequence[str | int | TypesDef],
        row: SrcRow,
    ) -> None:
        """Initialize the Source Interface class.

        Args
        ----
        endpoints: Sequence[...]: A sequence of EndPoint objects or
            sequences that define the interface. If a sequence of sequences is provided, each
            inner sequence should contain [ref_row, ref_idx, typ].
        """
        super().__init__(endpoints=endpoints, row=row)


class DstInterface(Interface):
    """Destination Interface class."""

    def __init__(
        self,
        endpoints: Sequence[EndPoint] | Sequence[list | tuple] | Sequence[str | int | TypesDef],
        row: DstRow,
    ) -> None:
        """Initialize the Destination Interface class.

        Args
        ----
        endpoints: Sequence[...]: A sequence of EndPoint objects or
            sequences that define the interface. If a sequence of sequences is provided, each
            inner sequence should contain [ref_row, ref_idx, typ].
        """
        super().__init__(endpoints=endpoints, row=row)
