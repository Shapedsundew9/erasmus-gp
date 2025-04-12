"""Common Erasmus GP Types."""

from enum import IntEnum, StrEnum
from typing import TypedDict  # pylint: disable=import-self

from egpcommon.common import NULL_TUPLE


class SrcRow(StrEnum):
    """Source rows."""

    I = "I"
    L = "L"
    A = "A"
    B = "B"


class DstRow(StrEnum):
    """Destination rows."""

    A = "A"
    B = "B"
    F = "F"
    L = "L"
    W = "W"
    O = "O"
    P = "P"
    U = "U"


class EPClsPostfix(StrEnum):
    """End Point Class postfixes."""

    SRC = "s"
    DST = "d"


class EndPointClass(IntEnum):
    """End Point Class."""

    SRC = True
    DST = False


class CPI(IntEnum):
    """Indices into a JSON Connection Graph End Point."""

    ROW = 0
    IDX = 1
    TYP = 2


Row = SrcRow | DstRow
SrcEndPointHash = str
DstEndPointHash = str
EndPointIndex = int
EndPointHash = SrcEndPointHash | DstEndPointHash | str


# Constants
DESTINATION_ROWS: tuple[DstRow, ...] = tuple(sorted(DstRow))
DESTINATION_ROW_SET: set[DstRow] = set(DstRow)
DESTINATION_ROW_SET_AND_U: set[str] = DESTINATION_ROW_SET | {"U"}
SOURCE_ROWS: tuple[SrcRow, ...] = tuple(sorted(SrcRow))
SOURCE_ROW_SET: set[SrcRow] = set(SrcRow)
DST_ONLY_ROWS: tuple[DstRow, ...] = tuple(
    sorted({DstRow.F, DstRow.O, DstRow.P})
)
SRC_ONLY_ROWS: tuple[SrcRow, ...] = tuple(sorted({SrcRow.I}))
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

VALID_ROW_SOURCES: tuple[dict[Row, tuple[SrcRow, ...]], dict[Row, tuple[SrcRow, ...]]] = (
    # No row F
    {
        SrcRow.I: NULL_TUPLE,
        DstRow.A: (SrcRow.I,),
        DstRow.B: (SrcRow.I, SrcRow.A),
        DstRow.O: (SrcRow.I, SrcRow.A, SrcRow.B),
    },
    # Has row F
    # F determines if the path through A or B is chosen
    {
        SrcRow.I: NULL_TUPLE,
        DstRow.F: (SrcRow.I,),
        DstRow.A: (SrcRow.I,),
        DstRow.B: (SrcRow.I,),
        DstRow.O: (SrcRow.I, SrcRow.A),
        DstRow.P: (SrcRow.I, SrcRow.B),
    },
)

VALID_DESTINATIONS: tuple[tuple[DstRow, ...], tuple[DstRow, ...]] = (
    (DstRow.A, DstRow.B, DstRow.O),
    (DstRow.F, DstRow.A, DstRow.B, DstRow.O, DstRow.P),
)

VALID_GRAPH_ROW_COMBINATIONS: set[str] = {
    "IABO",  # Standard
    "IFABOP",  # Conditional
    "IO",  # Codon or Empty
}

# Valid destination rows for a given row.
# The valid destination rows depends on whether there is a row F
VALID_ROW_DESTINATIONS: tuple[
    dict[Row, tuple[DstRow, ...]], dict[Row, tuple[DstRow, ...]]
] = (
    {  # No row F
        SrcRow.I: (DstRow.A, DstRow.B, DstRow.O),
        SrcRow.A: (DstRow.B, DstRow.O),
        SrcRow.B: (DstRow.O,),
        DstRow.O: NULL_TUPLE,
    },
    {  # Has row F
        SrcRow.I: (
            DstRow.F,
            DstRow.A,
            DstRow.B,
            DstRow.O,
            DstRow.P,
        ),
        SrcRow.A: (DstRow.O,),
        SrcRow.B: (DstRow.P,),
        DstRow.O: NULL_TUPLE,
        DstRow.P: NULL_TUPLE,
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
