"""The Interface Module."""

from __future__ import annotations
from typing import Sequence, Set as TypingSet, Any
from collections.abc import Iterable

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egppy.c_graph.c_graph_constants import Row, EndPointClass
from egppy.c_graph.end_point.end_point import EndPoint


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class Interface(FreezableObject):
    """The Interface class provides a base for defining interfaces in the EGP system."""

    __slots__ = ("endpoints", "_hash")

    def __init__(
        self,
        endpoints: Sequence[EndPoint] | Sequence[list | tuple],
        row: Row | None = None,
        frozen: bool = False,
    ) -> None:
        """Initialize the Interface class.

        Args
        ----
        endpoints: Sequence[EndPoint] | Sequence[Sequence]: A sequence of EndPoint objects or
            sequences that define the interface. If a sequence of sequences is provided, each
            inner sequence should contain [ref_row, ref_idx, typ] and the row parameter must
            be != None.
        row: Row | None: The destination row associated with the interface. Ignored if endpoints are
            provided as EndPoint objects.
        frozen: bool: If True, the object will be frozen after initialization.
            This allows the interface to be immutable after creation.
        """
        super().__init__(frozen=False)
        self.endpoints: list[EndPoint] | tuple[EndPoint, ...] = []

        # Validate row if endpoints are provided as sequences
        for idx, ep in enumerate(endpoints):
            if isinstance(ep, EndPoint):
                if ep.idx != idx:
                    raise ValueError(f"Endpoint index mismatch: {ep.idx} != {idx}")
                self.endpoints.append(ep)
            elif isinstance(ep, (list, tuple)):
                if len(ep) != 3:
                    raise ValueError(f"Invalid endpoint sequence length: {len(ep)} != 3")
                if row is None:
                    raise ValueError("Destination row must be specified if using sequence format.")
                self.endpoints.append(EndPoint(row=row, idx=idx, cls=EndPointClass.DST, typ=ep[2]))
            else:
                raise ValueError(f"Invalid endpoint format: {ep}")

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0
        if frozen:
            self.freeze()

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

    def cls(self) -> bool:
        """Return the class of the interface. Defaults to destination if no endpoints."""
        return self.endpoints[0].cls if self.endpoints else EndPointClass.DST

    def copy(self) -> Interface:
        """Return a copy of the interface."""
        return Interface(self.endpoints)

    def freeze(self, _fo_visited_in_freeze_call: TypingSet[int] | None = None) -> None:
        """Freeze the interface, making it immutable."""
        if not self._frozen:
            for ep in self.endpoints:
                ep.freeze()
            self.endpoints = tuple(self.endpoints)  # Convert to tuple for immutability
            self._hash = hash(self.endpoints)
            super().freeze()

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

    def ordered_td_uids(self) -> list[int]:
        """Return the ordered type definition UIDs."""
        return sorted(set(ep.typ.uid for ep in self.endpoints))

    def to_json(self) -> list[dict[str, Any]]:
        """Convert the interface to a JSON-compatible object."""
        return list(ep.to_json() for ep in self.endpoints)

    def to_td_uids(self) -> list[int]:
        """Convert the interface to a list of TypesDef UIDs (ints)."""
        return [ep.typ.uid for ep in self.endpoints]
