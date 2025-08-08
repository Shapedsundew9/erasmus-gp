"""The Interface Module."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Sequence

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egppy.genetic_code.c_graph_constants import (
    DESTINATION_ROW_SET,
    ROW_SET,
    SOURCE_ROW_SET,
    DstRow,
    EndPointClass,
    Row,
    SrcRow,
)
from egppy.genetic_code.end_point import EndPoint, TypesDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


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


class Interface(FreezableObject):
    """The Interface class provides a base for defining interfaces in the EGP system."""

    __slots__ = ("endpoints", "_hash")

    def __init__(
        self,
        endpoints: Sequence[EndPoint] | Sequence[list | tuple] | Sequence[str | int | TypesDef],
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
        row: Row | None: The destination row associated with the interface. Ignored if endpoints are
            provided as EndPoint objects.
        frozen: bool: If True, the object will be frozen after initialization.
            This allows the interface to be immutable after creation.
        """
        super().__init__(frozen=False)
        self.endpoints: list[EndPoint] | tuple[EndPoint, ...] = []

        # Validate row if endpoints are provided as sequences
        row_cls = (
            EndPointClass.DST if row is None or row in DESTINATION_ROW_SET else EndPointClass.SRC
        )
        for idx, ep in enumerate(endpoints):
            if isinstance(ep, EndPoint):
                if ep.idx != idx:
                    raise ValueError(f"Endpoint index mismatch: {ep.idx} != {idx}")
                self.endpoints.append(ep)
            elif isinstance(ep, (list, tuple)):
                if len(ep) != 3:
                    raise ValueError(f"Invalid endpoint sequence length: {len(ep)} != 3")
                if row is None or row_cls == EndPointClass.SRC:
                    raise ValueError("Destination row must be specified if using triplet format.")
                self.endpoints.append(EndPoint(row=row, idx=idx, cls=EndPointClass.DST, typ=ep[2]))
            elif isinstance(ep, (str, int, TypesDef)):
                if row is None:
                    raise ValueError("Row must be specified if using EGP types.")
                self.endpoints.append(EndPoint(row=row, idx=idx, cls=row_cls, typ=ep))
            else:
                raise ValueError(
                    f"Invalid endpoint type: {type(ep)} was expecting EndPoint or Sequence"
                )

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0

    def __eq__(self, value: object) -> bool:
        """Check equality of Interface instances."""
        if not isinstance(value, Interface):
            return False
        return self.endpoints == value.endpoints

    def __hash__(self) -> int:
        """Return the hash of the interface."""
        if self.is_frozen():
            # Use the persistent hash if the interface is frozen. Hash is defined in self.freeze()
            return self._hash
        # If not frozen, calculate the hash dynamically
        return hash(tuple(self.endpoints))

    def __getitem__(self, idx: int) -> EndPoint:
        """Get an endpoint by index."""
        return self.endpoints[idx]

    def __iter__(self) -> Iterable[EndPoint]:
        """Return an iterator over the endpoints."""
        return iter(self.endpoints)

    def __len__(self) -> int:
        """Return the number of endpoints in the interface."""
        return len(self.endpoints)

    def __setitem__(self, idx: int, value: EndPoint) -> None:
        """Set an endpoint at a specific index."""
        if _logger.isEnabledFor(level=DEBUG):
            if self.is_frozen():
                raise RuntimeError("Cannot modify a frozen Interface")
            if not isinstance(value, EndPoint):
                raise TypeError(f"Expected EndPoint, got {type(value)}")
            if idx < 0 or idx >= len(self.endpoints):
                raise IndexError("Index out of range")
        assert isinstance(self.endpoints, list), "Endpoints must be a list to allow item assignment"
        self.endpoints[idx] = value

    def __str__(self) -> str:
        """Return the string representation of the interface."""
        return f"Interface({', '.join(str(ep.typ) for ep in self.endpoints)})"

    def cls(self) -> EndPointClass:
        """Return the class of the interface. Defaults to destination if no endpoints."""
        return self.endpoints[0].cls if self.endpoints else EndPointClass.DST

    def copy(self) -> Interface:
        """Return a modifiable shallow copy of the interface."""
        return Interface(self.endpoints)

    def freeze(self, store: bool = True) -> Interface:
        """Freeze the interface, making it immutable."""
        if not self._frozen:
            self.endpoints = tuple(ep.freeze() for ep in self.endpoints)
            retval = super().freeze(store)
            # Need to jump through hoops to set the persistent hash
            object.__setattr__(self, "_hash", hash(self.endpoints))

            # Some sanity checks
            if _logger.isEnabledFor(level=VERIFY):
                if not len(self.endpoints) > 0:
                    raise ValueError("Interface must have at least one endpoint.")
                if not all(isinstance(ep, EndPoint) for ep in self.endpoints):
                    raise ValueError("All endpoints must be EndPoint instances.")
                if not all(ep.row == self.endpoints[0].row for ep in self.endpoints):
                    raise ValueError("All endpoints must have the same row.")
                if not all(ep.cls == self.endpoints[0].cls for ep in self.endpoints):
                    raise ValueError("All endpoints must have the same class.")
            return retval
        return self

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

    def unconnected_eps(self) -> list[EndPoint]:
        """Return a list of unconnected endpoints."""
        return [ep for ep in self.endpoints if not ep.is_connected()]


# The NULL Interface, used as a placeholder.
NULL_INTERFACE: Interface = Interface(endpoints=[]).freeze()
