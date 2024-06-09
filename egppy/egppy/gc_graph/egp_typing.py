"""Common Erasmus GP Types."""

from enum import IntEnum
from typing import Any, Literal, LiteralString, TypedDict, TypeGuard

DestinationRow = Literal["A", "B", "F", "O", "P"]
SourceRow = Literal["I", "A", "B"]
Row = DestinationRow | SourceRow
EndPointClass = bool
EndPointClassStr = Literal["s", "d"]
SrcEndPointHash = str
DstEndPointHash = str
EndPointIndex = int
EndPointType = int
EndPointHash = SrcEndPointHash | DstEndPointHash | str


# Constants
SRC_EP: Literal[True] = True
DST_EP: Literal[False] = False
SRC_EP_CLS_STR: Literal["s"] = "s"
DST_EP_CLS_STR: Literal["d"] = "d"
EP_CLS_STR_TUPLE: tuple[Literal["d"], Literal["s"]] = (DST_EP_CLS_STR, SRC_EP_CLS_STR)
DESTINATION_ROWS: tuple[DestinationRow, ...] = ("F", "A", "B", "O", "P")
SOURCE_ROWS: tuple[SourceRow, ...] = ("I", "A", "B")
ROWS: tuple[Row, ...] = tuple(sorted({*SOURCE_ROWS, *DESTINATION_ROWS}))
ALL_ROWS_STR: LiteralString = "".join(ROWS)

# Indices for source and destination rows must match the order of the rows in the tuple.
ROWS_INDEXED: tuple[Row, ...] = ("I", "A", "B", "F", "A", "B", "O", "P")
ROW_CLS_INDEXED: tuple[str, ...] = ("Is", "As", "Bs", "Fd", "Ad", "Bd", "Od", "Pd")


class SrcRowIndex(IntEnum):
    """Indices for source rows."""

    I = ROW_CLS_INDEXED.index("Is")
    A = ROW_CLS_INDEXED.index("As")
    B = ROW_CLS_INDEXED.index("Bs")


class DstRowIndex(IntEnum):
    """Indices for destination rows."""

    F = ROW_CLS_INDEXED.index("Fd")
    A = ROW_CLS_INDEXED.index("Ad")
    B = ROW_CLS_INDEXED.index("Bd")
    O = ROW_CLS_INDEXED.index("Od")
    P = ROW_CLS_INDEXED.index("Pd")


GRAPH_ROW_INDEX_ORDER: tuple[
    SrcRowIndex, DstRowIndex, DstRowIndex, SrcRowIndex, DstRowIndex, SrcRowIndex, DstRowIndex, DstRowIndex
] = (
    SrcRowIndex.I,
    DstRowIndex.F,
    DstRowIndex.A,
    SrcRowIndex.A,
    DstRowIndex.B,
    SrcRowIndex.B,
    DstRowIndex.O,
    DstRowIndex.P,
)

SOURCE_ROW_INDEXES: dict[SourceRow, SrcRowIndex] = {
    "I": SrcRowIndex.I,
    "A": SrcRowIndex.A,
    "B": SrcRowIndex.B,
}
DESTINATION_ROW_INDEXES: dict[DestinationRow, DstRowIndex] = {
    "F": DstRowIndex.F,
    "A": DstRowIndex.A,
    "B": DstRowIndex.B,
    "O": DstRowIndex.O,
    "P": DstRowIndex.P,
}
SOURCE_ROW_LETTERS: dict[SrcRowIndex, SourceRow] = {
    SrcRowIndex.I: "I",
    SrcRowIndex.A: "A",
    SrcRowIndex.B: "B",
}
DESTINATION_ROW_LETTERS: dict[DstRowIndex, DestinationRow] = {
    DstRowIndex.F: "F",
    DstRowIndex.A: "A",
    DstRowIndex.B: "B",
    DstRowIndex.O: "O",
    DstRowIndex.P: "P",
}

# Valid source rows for a given row.
# The valid source rows depends on whether there is a row F
VALID_ROW_SOURCES: tuple[dict[Row, tuple[SourceRow, ...]], dict[Row, tuple[SourceRow, ...]]] = (
    # No row F
    {
        "I": tuple(),
        "A": ("I",),
        "B": ("I", "A"),
        "O": ("I", "A", "B"),
    },
    # Has row F
    # F determines if the path through A or B is chosen
    {
        "I": tuple(),
        "F": ("I",),
        "A": ("I",),
        "B": ("I",),
        "O": ("I", "A"),
        "P": ("I", "B"),
    },
)
VALID_DESTINATIONS: tuple[tuple[DestinationRow, ...], tuple[DestinationRow, ...]] = (
    ("A", "B", "O"), ("F", "A", "B", "O", "P"))

# Valid graph row combinations.
# NB: These rules define a valid graph not necessarily a stable graph.
# Rules:
#   1. If row F is present then row P must be present
#   3. P cannot be present unless F is present
#   4. Row B cannot exist without row A
#   5. Row F cannot exists without row A
#   6. A graph must have an interface i.e. row I or row O (or both)
#   7. Row O cannot exist without any source rows.
#   8. A null graph (one with no rows) is invalid.
#   9. Rows must be explicitly defined (no implied rows)
#
# Derived by:
"""
from itertools import combinations
combos = []
for c in [''.join(sorted(s)) for n in range(7) for s in combinations("ABCFIOP", n)]:
    if "F" in c and "I" not in c:
        continue
    if "F" in c and "O" in c and "P" not in c:
        continue
    if "P" in c and ("F" not in c or "O" not in c):
        continue
    if ("F" in c or "B" in c) and "A" not in c:
        continue
    if "O" not in c and "I" not in c:
        continue
    if c == "" or c == "O":
        continue
    combos.append(c)
"""
VALID_GRAPH_ROW_COMBINATIONS: set[str] = {
    "I",
    "AI",
    "AO",
    "IO",
    "ABI",
    "ABO",
    "ACI",
    "ACO",
    "AFI",
    "AIO",
    "ABCI",
    "ABCO",
    "ABFI",
    "ABIO",
    "ACFI",
    "ACIO",
    "ABCFI",
    "ABCIO",
    "AFIOP",
    "ABFIOP",
    "ACFIOP",
}


def isDestinationRow(row: Row) -> TypeGuard[DestinationRow]:
    """Narrow a row to a destination row."""
    return row in DESTINATION_ROWS


# Valid destination rows for a given row.
# The valid destination rows depends on whether there is a row F
VALID_ROW_DESTINATIONS: tuple[dict[Row, tuple[DestinationRow, ...]], dict[Row, tuple[DestinationRow, ...]]] = (
    # No row F
    {k: tuple(d for d, s in VALID_ROW_SOURCES[False].items() if k in s and isDestinationRow(d)) for k in ROWS},
    # Has row F
    # F determines if the path through A or B is chosen
    {k: tuple(d for d, s in VALID_ROW_SOURCES[True].items() if k in s and isDestinationRow(d)) for k in ROWS},
)


class CPI(IntEnum):
    """Indices into a ConnectionPoint."""

    ROW = 0
    IDX = 1
    TYP = 2


class CVI(IntEnum):
    """Indices into a ConstantValue."""

    VAL = 0
    TYP = 1


class PairIdx(IntEnum):
    """Indices into *Pair."""

    ROW = 0
    VALUES = 1


# A ConnectionGraph is the graph defined in the GC GMS.
# It is a dict of Destination Rows (or constant value row - which makes things a bit more awkward)
# with a list of the Source row references + type that connect to it.
ConstantExecStr = str
ConstantValue = tuple[ConstantExecStr, EndPointType]
ConstantRow = list[ConstantValue]
ConstantPair = tuple[Literal["C"], ConstantRow]
JSONGraph = dict[
    DestinationRow | Literal["C"],
    list[list[SourceRow | EndPointIndex | EndPointType]] | list[list[ConstantExecStr | EndPointType]],
]


def isConstantPair(obj: tuple[str, Any]) -> TypeGuard[ConstantPair]:
    """Narrow a connection graph key:value pair to a constant row."""
    return obj[0] == "C"


class EndPointTypeLookupFile(TypedDict):
    """Format of the egp_type.json file."""

    n2v: dict[str, int]
    v2n: dict[str, str]
    instanciation: dict[str, list[str | bool | None]]


def isInstanciationValue(
    obj,
) -> TypeGuard[tuple[str | None, str | None, str | None, str | None, bool, str]]:
    """Is obj an instance of an instanciation definition."""
    if not isinstance(obj, (tuple, list)):
        return False
    if not len(obj) == 6:
        return False
    if not all((isinstance(element, str) or element is None for element in obj[:4])):
        return False
    return isinstance(obj[4], bool) and isinstance(obj[5], str)


InstanciationType = tuple[str | None, str | None, str | None, str | None, bool, str]


class EndPointTypeLookup(TypedDict):
    """Format of the ep_type_lookup structure."""

    n2v: dict[str, int]  # End point type name: End point type value
    v2n: dict[int, str]  # End point type value: End point type name

    # End point type value: package, version, module, name, default can take parameters
    instanciation: dict[int, InstanciationType]
