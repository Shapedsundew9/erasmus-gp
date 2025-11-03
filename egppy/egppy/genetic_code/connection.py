"""Connection class for representing connections between endpoints in a connection graph."""

from __future__ import annotations

from egpcommon.egp_log import VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egpcommon.object_deduplicator import ObjectDeduplicator
from egppy.genetic_code.c_graph_constants import DESTINATION_ROW_SET, SOURCE_ROW_SET, DstRow, SrcRow

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)

# Create object deduplicator for Connection objects
connection_store = ObjectDeduplicator("Connection store", 2**14)


class Connection(FreezableObject):
    """Represents a connection between two endpoints in a connection graph.

    A connection links a source endpoint (src_row, src_idx) to a destination
    endpoint (dst_row, dst_idx). Connections are immutable once frozen and can
    be deduplicated for memory efficiency.

    The connection is directional: source -> destination.
    """

    __slots__ = ("src_row", "src_idx", "dst_row", "dst_idx", "_hash")

    def __init__(
        self,
        src_row: SrcRow | str,
        src_idx: int,
        dst_row: DstRow | str,
        dst_idx: int,
        frozen: bool = False,
    ) -> None:
        """Initialize a connection between two endpoints.

        Args
        ----
        src_row: SrcRow | str: The source row (e.g., SrcRow.I, "I")
        src_idx: int: The source endpoint index (0-255)
        dst_row: DstRow | str: The destination row (e.g., DstRow.A, "A")
        dst_idx: int: The destination endpoint index (0-255)
        frozen: bool: If True, freeze the connection immediately after creation
        """
        super().__init__(frozen=False)

        # Validate and normalize rows
        if isinstance(src_row, str):
            if src_row not in SOURCE_ROW_SET:
                raise ValueError(f"Invalid source row: {src_row}")
            src_row = SrcRow(src_row)
        if isinstance(dst_row, str):
            if dst_row not in DESTINATION_ROW_SET:
                raise ValueError(f"Invalid destination row: {dst_row}")
            dst_row = DstRow(dst_row)

        # Validate indices
        if not isinstance(src_idx, int) or not (0 <= src_idx < 256):
            raise ValueError(f"Source index must be an integer between 0 and 255, got {src_idx}")
        if not isinstance(dst_idx, int) or not (0 <= dst_idx < 256):
            raise ValueError(
                f"Destination index must be an integer between 0 and 255, got {dst_idx}"
            )

        self.src_row: SrcRow = src_row
        self.src_idx: int = src_idx
        self.dst_row: DstRow = dst_row
        self.dst_idx: int = dst_idx

        # Persistent hash will be defined when frozen. Dynamic until then.
        self._hash: int = 0

        if frozen:
            self.freeze()

    def __eq__(self, value: object) -> bool:
        """Check equality of Connection instances."""
        if not isinstance(value, Connection):
            return False
        return (
            self.src_row == value.src_row
            and self.src_idx == value.src_idx
            and self.dst_row == value.dst_row
            and self.dst_idx == value.dst_idx
        )

    def __hash__(self) -> int:
        """Return the hash of the connection."""
        if self.is_frozen():
            # Hash is defined in self.freeze() to ensure immutability
            return self._hash
        # Else it is dynamically defined.
        return hash((self.src_row, self.src_idx, self.dst_row, self.dst_idx))

    def __ne__(self, value: object) -> bool:
        """Check inequality of Connection instances."""
        return not self.__eq__(value)

    def __str__(self) -> str:
        """Return the string representation of the connection."""
        return (
            f"Connection({self.src_row}{self.src_idx:03d} -> " f"{self.dst_row}{self.dst_idx:03d})"
        )

    def __repr__(self) -> str:
        """Return the detailed representation of the connection."""
        return (
            f"Connection(src_row={self.src_row}, src_idx={self.src_idx}, "
            f"dst_row={self.dst_row}, dst_idx={self.dst_idx})"
        )

    def freeze(self, store: bool = True) -> Connection:
        """Freeze the connection, making it immutable.

        Args
        ----
        store: bool: If True, store the frozen connection in the deduplicator.

        Returns
        -------
        Connection: The frozen connection (may be a different instance if deduplicated).
        """
        if not self.is_frozen():
            retval = super().freeze(store)
            # Need to jump through hoops to set the persistent hash
            object.__setattr__(
                self, "_hash", hash((self.src_row, self.src_idx, self.dst_row, self.dst_idx))
            )

            # Some sanity checks
            if _logger.isEnabledFor(level=VERIFY):
                if self.src_row not in SOURCE_ROW_SET:
                    raise ValueError(f"Source row must be in SOURCE_ROW_SET, got {self.src_row}")
                if self.dst_row not in DESTINATION_ROW_SET:
                    raise ValueError(
                        f"Destination row must be in DESTINATION_ROW_SET, got {self.dst_row}"
                    )
                if not (0 <= self.src_idx < 256):
                    raise ValueError(f"Source index must be between 0 and 255, got {self.src_idx}")
                if not (0 <= self.dst_idx < 256):
                    raise ValueError(
                        f"Destination index must be between 0 and 255, got {self.dst_idx}"
                    )
            return retval
        return self

    def to_ref(self) -> tuple[str, int]:
        """Convert the source endpoint to a reference tuple.

        Returns
        -------
        tuple[str, int]: A tuple of (src_row, src_idx) representing the source endpoint.
        """
        return (str(self.src_row), self.src_idx)

    def to_list(self) -> list[str | int]:
        """Convert the source endpoint to a reference list.

        Returns
        -------
        list[str | int]: A list of [src_row, src_idx] representing the source endpoint.
        """
        return [str(self.src_row), self.src_idx]

    def to_json(self) -> dict:
        """Convert the connection to a JSON-compatible object.

        Returns
        -------
        dict: A dictionary representation of the connection.
        """
        return {
            "src_row": str(self.src_row),
            "src_idx": self.src_idx,
            "dst_row": str(self.dst_row),
            "dst_idx": self.dst_idx,
        }

    def verify(self) -> None:
        """Verify the integrity of the connection.

        Raises
        ------
        ValueError: If any validation check fails.
        """
        if self.src_row not in SOURCE_ROW_SET:
            raise ValueError(f"Source row must be in SOURCE_ROW_SET, got {self.src_row}")
        if self.dst_row not in DESTINATION_ROW_SET:
            raise ValueError(f"Destination row must be in DESTINATION_ROW_SET, got {self.dst_row}")
        if not (0 <= self.src_idx < 256):
            raise ValueError(f"Source index must be between 0 and 255, got {self.src_idx}")
        if not (0 <= self.dst_idx < 256):
            raise ValueError(f"Destination index must be between 0 and 255, got {self.dst_idx}")

        # Call parent verify
        super().verify()


def create_connection_from_ref(
    ref: list[str | int] | tuple[str, int], dst_row: DstRow | str, dst_idx: int
) -> Connection:
    """Create a Connection from a reference tuple/list and destination.

    Args
    ----
    ref: list[str | int] | tuple[str, int]: The source reference [src_row, src_idx]
    dst_row: DstRow | str: The destination row
    dst_idx: int: The destination endpoint index

    Returns
    -------
    Connection: A new Connection object.
    """
    if not isinstance(ref, (list, tuple)) or len(ref) != 2:
        raise ValueError(f"Reference must be a list or tuple of length 2, got {ref}")

    src_row = ref[0]
    src_idx = ref[1]

    if not isinstance(src_row, str):
        raise TypeError(f"Source row must be a string, got {type(src_row)}")
    if not isinstance(src_idx, int):
        raise TypeError(f"Source index must be an int, got {type(src_idx)}")

    return Connection(src_row, src_idx, dst_row, dst_idx)
