"""Common Erasmus GP Types."""

from enum import IntEnum, StrEnum


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
JSONRef = list[str | int]  # e.g. ["A", 0, "int"] or ["I", 0, "int"]
JSONRefRow = list[JSONRef]
JSONCGraph = dict[DstRow, JSONRefRow]


# The minimum JSON graph.
EMPTY_JSON_CGRAPH: JSONCGraph = {DstRow.O: [], DstRow.U: []}


# Constants
DESTINATION_ROWS: tuple[DstRow, ...] = tuple(sorted(DstRow))
DESTINATION_ROW_MAP: dict[str, DstRow] = {str(row): row for row in DESTINATION_ROWS}
DESTINATION_ROW_SET: set[DstRow] = set(DstRow)
DESTINATION_ROW_SET_AND_U: set[str] = DESTINATION_ROW_SET | {"U"}
SOURCE_ROWS: tuple[SrcRow, ...] = tuple(sorted(SrcRow))
SOURCE_ROW_MAP: dict[str, SrcRow] = {str(row): row for row in SOURCE_ROWS}
SOURCE_ROW_SET: set[SrcRow] = set(SrcRow)
DST_ONLY_ROWS: tuple[DstRow, ...] = tuple(
    sorted({DstRow.F, DstRow.O, DstRow.P, DstRow.W, DstRow.U})
)
SRC_ONLY_ROWS: tuple[SrcRow, ...] = tuple(sorted({SrcRow.I}))
ROWS: tuple[Row, ...] = tuple(sorted({*SOURCE_ROWS, *DESTINATION_ROWS}))
ROW_MAP: dict[str, SrcRow | DstRow] = {str(row): row for row in ROWS}
ROW_SET: set[Row] = set(ROWS)
EPC_STR_TUPLE: tuple[EPClsPostfix, EPClsPostfix] = (EPClsPostfix.DST, EPClsPostfix.SRC)
EPC_MAP: dict[str, EndPointClass] = {"s": EndPointClass.SRC, "d": EndPointClass.DST}
ALL_ROWS_STR: str = "".join(ROWS)
ROW_CLS_INDEXED: tuple[str, ...] = tuple(f"{row}{EPClsPostfix.SRC}" for row in SOURCE_ROWS) + tuple(
    f"{row}{EPClsPostfix.DST}" for row in DESTINATION_ROWS
)
