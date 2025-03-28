"""Common Erasmus GP Types."""

from enum import IntEnum, StrEnum
from typing import TypedDict  # pylint: disable=import-self

from egpcommon.common import NULL_TUPLE


class SourceRow(StrEnum):
    """Source rows."""

    I = "I"
    A = "A"
    B = "B"


class DestinationRow(StrEnum):
    """Destination rows."""

    A = "A"
    B = "B"
    F = "F"
    O = "O"
    P = "P"


class EPClsPostfix(StrEnum):
    """End Point Class postfixes."""

    SRC = "s"
    DST = "d"


class EndPointClass(IntEnum):
    """End Point Class."""

    SRC = True
    DST = False


class CPI(IntEnum):
    """Indices into a JSON GC Graph End Point."""

    ROW = 0
    IDX = 1
    TYP = 2


Row = SourceRow | DestinationRow
SrcEndPointHash = str
DstEndPointHash = str
EndPointIndex = int
EndPointHash = SrcEndPointHash | DstEndPointHash | str


# Constants
DESTINATION_ROWS: tuple[DestinationRow, ...] = tuple(sorted(DestinationRow))
DESTINATION_ROW_SET: set[DestinationRow] = set(DestinationRow)
DESTINATION_ROW_SET_AND_U: set[str] = DESTINATION_ROW_SET | {"U"}
SOURCE_ROWS: tuple[SourceRow, ...] = tuple(sorted(SourceRow))
SOURCE_ROW_SET: set[SourceRow] = set(SourceRow)
DST_ONLY_ROWS: tuple[DestinationRow, ...] = tuple(
    sorted({DestinationRow.F, DestinationRow.O, DestinationRow.P})
)
SRC_ONLY_ROWS: tuple[SourceRow, ...] = tuple(sorted({SourceRow.I}))
ROWS: tuple[Row, ...] = tuple(sorted({*SOURCE_ROWS, *DESTINATION_ROWS}))
ROW_SET: set[Row] = set(ROWS)
EP_CLS_STR_TUPLE: tuple[EPClsPostfix, EPClsPostfix] = (EPClsPostfix.DST, EPClsPostfix.SRC)
ALL_ROWS_STR: str = "".join(ROWS)
GRAPH_ORDER: str = "IFABOP"
ROW_CLS_INDEXED: tuple[str, ...] = tuple(f"{row}{EPClsPostfix.SRC}" for row in SOURCE_ROWS) + tuple(
    f"{row}{EPClsPostfix.DST}" for row in DESTINATION_ROWS
)
# Valid source rows for a given row.
# The valid source rows depends on whether there is a row F

VALID_ROW_SOURCES: tuple[dict[Row, tuple[SourceRow, ...]], dict[Row, tuple[SourceRow, ...]]] = (
    # No row F
    {
        SourceRow.I: NULL_TUPLE,
        DestinationRow.A: (SourceRow.I,),
        DestinationRow.B: (SourceRow.I, SourceRow.A),
        DestinationRow.O: (SourceRow.I, SourceRow.A, SourceRow.B),
    },
    # Has row F
    # F determines if the path through A or B is chosen
    {
        SourceRow.I: NULL_TUPLE,
        DestinationRow.F: (SourceRow.I,),
        DestinationRow.A: (SourceRow.I,),
        DestinationRow.B: (SourceRow.I,),
        DestinationRow.O: (SourceRow.I, SourceRow.A),
        DestinationRow.P: (SourceRow.I, SourceRow.B),
    },
)

VALID_DESTINATIONS: tuple[tuple[DestinationRow, ...], tuple[DestinationRow, ...]] = (
    (DestinationRow.A, DestinationRow.B, DestinationRow.O),
    (DestinationRow.F, DestinationRow.A, DestinationRow.B, DestinationRow.O, DestinationRow.P),
)

VALID_GRAPH_ROW_COMBINATIONS: set[str] = {
    "IABO",  # Standard
    "IFABOP",  # Conditional
    "IO",  # Codon or Empty
}

# Valid destination rows for a given row.
# The valid destination rows depends on whether there is a row F
VALID_ROW_DESTINATIONS: tuple[
    dict[Row, tuple[DestinationRow, ...]], dict[Row, tuple[DestinationRow, ...]]
] = (
    {  # No row F
        SourceRow.I: (DestinationRow.A, DestinationRow.B, DestinationRow.O),
        SourceRow.A: (DestinationRow.B, DestinationRow.O),
        SourceRow.B: (DestinationRow.O,),
        DestinationRow.O: NULL_TUPLE,
    },
    {  # Has row F
        SourceRow.I: (
            DestinationRow.F,
            DestinationRow.A,
            DestinationRow.B,
            DestinationRow.O,
            DestinationRow.P,
        ),
        SourceRow.A: (DestinationRow.O,),
        SourceRow.B: (DestinationRow.P,),
        DestinationRow.O: NULL_TUPLE,
        DestinationRow.P: NULL_TUPLE,
    },
)


class EndPointTypeLookupFile(TypedDict):
    """Format of the egp_type.json file."""

    n2v: dict[str, int]
    v2n: dict[str, str]
    instanciation: dict[str, list[str | bool | None]]


InstanciationType = tuple[str | None, str | None, str | None, str | None, bool, str]


class EndPointTypeLookup(TypedDict):
    """Format of the ep_type_lookup structure."""

    n2v: dict[str, int]  # End point type name: End point type value
    v2n: dict[int, str]  # End point type value: End point type name

    # End point type value: package, version, module, name, default can take parameters
    instanciation: dict[int, InstanciationType]


def str2epcls(ep_cls_str: str) -> EndPointClass:
    """Convert an end point class string to an end point class integer."""
    return EndPointClass.SRC if ep_cls_str == EPClsPostfix.SRC else EndPointClass.DST
