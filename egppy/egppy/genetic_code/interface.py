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
    EndPointClass,
    Row,
    SrcRow,
)
from egppy.genetic_code.endpoint import EndPoint, TypesDef
from egppy.genetic_code.endpoint_abc import EndPointABC, EndpointMemberType
from egppy.genetic_code.interface_abc import InterfaceABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def unpack_ref(ref: list[int | str] | tuple[str, int]) -> tuple[str, int]:
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


def unpack_src_ref(ref: list[int | str] | tuple[str, int]) -> tuple[SrcRow, int]:
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


def unpack_dst_ref(ref: list[int | str] | tuple[str, int]) -> tuple[DstRow, int]:
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


class Interface(CommonObj, InterfaceABC):
    """The Interface class provides a base for defining interfaces in the EGP system."""

    __slots__ = ("endpoints", "_hash")

    def __init__(
        self,
        endpoints: (
            Sequence[EndPoint]
            | Sequence[EndpointMemberType]
            | Sequence[list | tuple]
            | Sequence[str | int | TypesDef]
            | InterfaceABC
        ),
        row: Row | None = None,
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
        row: Row | None: The destination row associated with the interface. Ignored if endpoints are
            provided as EndPoint objects.
        """
        super().__init__()
        self.endpoints: list[EndPoint] = []

        # Validate row if endpoints are provided as sequences
        row_cls = EndPointClass.DST if row is None or isinstance(row, DstRow) else EndPointClass.SRC
        for idx, ep in enumerate(endpoints):
            if isinstance(ep, EndPointABC):
                # Have to make a copy to ensure mutability & independence
                self.endpoints.append(EndPoint(ep))
            elif isinstance(ep, (list, tuple)):
                if len(ep) == 3:
                    if row is None:
                        raise ValueError(
                            "Row parameter must be provided when endpoints are sequences"
                        )
                    self.endpoints.append(
                        EndPoint(row, idx, EndPointClass.DST, ep[2], ((ep[0], ep[1]),))
                    )
                else:
                    # EndPointMemberType
                    self.endpoints.append(EndPoint(*ep))
            elif isinstance(ep, (str, int, TypesDef)):
                self.endpoints.append(EndPoint(row, idx, row_cls, ep, None))
            else:
                raise ValueError(
                    f"Invalid endpoint type: {type(ep)} was expecting EndPoint or Sequence"
                )
        self._hash: int = 0

    def __eq__(self, value: object) -> bool:
        """Check equality of Interface instances.
        This implements deep equality checking between two Interface instances
        which can be quite expensive for large interfaces.
        """
        if not isinstance(value, InterfaceABC):
            return False
        if len(self) != len(value):
            return False
        return all(a == b for a, b in zip(self, value))

    def __hash__(self) -> int:
        """Return the hash of the interface."""
        return hash(tuple(hash(ep) for ep in self.endpoints))

    def __add__(self, other: InterfaceABC) -> InterfaceABC:
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
        if not isinstance(other, InterfaceABC):
            raise TypeError(f"Can only add InterfaceABC to InterfaceABC, got {type(other)}")

        # Handle empty interfaces
        if len(self.endpoints) == 0:
            return Interface(other)
        if len(other) == 0:
            return Interface(self)

        # Create new interface with copied endpoints from both
        # Create copies of endpoints with updated indices (with clean references)
        new_iface = Interface(self)
        new_iface.extend(other)
        return new_iface

    def __getitem__(self, idx: int) -> EndPointABC:
        """Get an endpoint by index."""
        return self.endpoints[idx]

    def __iter__(self) -> Iterator[EndPointABC]:
        """Return an iterator over the endpoints."""
        return iter(self.endpoints)

    def __len__(self) -> int:
        """Return the number of endpoints in the interface."""
        return len(self.endpoints)

    def __setitem__(self, idx: int, value: EndPointABC) -> None:
        """Set an endpoint at a specific index.

        Args
        ----
        idx: int: The index at which to set the endpoint.
        value: EndPoint: The endpoint to set.

        Raises
        ------
        RuntimeError: If the interface is frozen.
        TypeError: If value is not an EndPoint instance.
        IndexError: If idx is out of range.
        ValueError: If the endpoint's row or class doesn't match existing endpoints.
        """
        if not isinstance(value, EndPointABC):
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

    def append(self, value: EndPointABC) -> None:
        """Append an endpoint to the interface.

        Append correctly sets the index of the appended endpoint.
        However, it does not change the row or class of the endpoint.

        Args
        ----
        value: EndPointABC: The endpoint to append.
        """
        _value = EndPoint(value)  # Make a copy to ensure mutability & independence
        _value.idx = len(self.endpoints)  # Ensure the index is correct
        self.endpoints.append(_value)

    def cls(self) -> EndPointClass:
        """Return the class of the interface. Defaults to destination if no endpoints."""
        return self.endpoints[0].cls if self.endpoints else EndPointClass.DST

    def extend(self, values: list[EndPointABC] | tuple[EndPointABC, ...] | InterfaceABC) -> None:
        """Extend the interface with multiple endpoints.

        Extend correctly sets the indices of the appended endpoints.
        However, it does not change the row or class of the endpoint.

        Args
        ----
        values: list[EndPoint] | tuple[EndPoint, ...]: The endpoints to add.
        """
        for idx, value in enumerate(values, start=len(self.endpoints)):
            _value = EndPoint(value)  # Make a copy to ensure mutability & independence
            _value.idx = idx  # Ensure the index is correct
            self.endpoints.append(_value)

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
        first_row = self.endpoints[0].row
        if not all(ep.row == first_row for ep in self.endpoints):
            raise ValueError(f"All endpoints must have the same row. Expected {first_row}.")

        # Check all endpoints have the same class
        first_cls = self.endpoints[0].cls
        if not all(ep.cls == first_cls for ep in self.endpoints):
            raise ValueError(f"All endpoints must have the same class. Expected {first_cls}.")

        # Verify each endpoint
        for ep in self.endpoints:
            ep.verify()

        # Call parent verify() which will trigger consistency() if CONSISTENCY logging is enabled
        super().verify()

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

    def types(self) -> tuple[list[int], bytes]:
        """Return a tuple of the ordered type UIDs and the indices into to it."""
        otu: list[int] = self.ordered_td_uids()
        lookup_indices: dict[int, int] = {uid: idx for idx, uid in enumerate(otu)}
        indices = bytes(lookup_indices[ep.typ.uid] for ep in self.endpoints)
        return otu, indices

    def ordered_td_uids(self) -> list[int]:
        """Return the ordered type definition UIDs."""
        return sorted(set(ep.typ.uid for ep in self.endpoints))

    def to_json(self, json_c_graph: bool = False) -> list:
        """Convert the interface to a JSON-compatible object.
        If `json_c_graph` is True, it returns a list suitable for JSON Connection Graph format.
        """
        return [ep.to_json(json_c_graph=json_c_graph) for ep in self.endpoints]

    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints)."""
        return [ep.typ.uid for ep in self.endpoints]

    def unconnected_eps(self) -> list[EndPointABC]:
        """Return a list of unconnected endpoints."""
        return [ep for ep in self.endpoints if not ep.is_connected()]

    def set_cls(self, ep_cls) -> InterfaceABC:
        """Set the class of all endpoints in the interface."""
        for ep in self.endpoints:
            ep.cls = ep_cls
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
        for ep in self.endpoints:
            ep.row = row
        return self

    def clr_refs(self) -> InterfaceABC:
        """Clear all references in the interface endpoints.
        Returns:
            Interface: Self with all endpoint references cleared."""
        for ep in self.endpoints:
            ep.clr_refs()
        return self

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


# Re-use the Interface object deduplicator for both SrcInterface and DstInterface
class SrcInterface(Interface):
    """Source Interface class."""

    def __init__(
        self,
        endpoints: Sequence[EndPoint] | Sequence[list | tuple] | Sequence[str | int | TypesDef],
        row: SrcRow | None = None,
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
        row: DstRow | None = None,
    ) -> None:
        """Initialize the Destination Interface class.

        Args
        ----
        endpoints: Sequence[...]: A sequence of EndPoint objects or
            sequences that define the interface. If a sequence of sequences is provided, each
            inner sequence should contain [ref_row, ref_idx, typ].
        """
        super().__init__(endpoints=endpoints, row=row)
