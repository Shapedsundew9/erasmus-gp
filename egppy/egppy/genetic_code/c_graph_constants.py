"""Common Erasmus GP Types."""

from enum import IntEnum, StrEnum
from itertools import chain


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


class SrcIfKey(StrEnum):
    """Source Interfaces."""

    IS = SrcRow.I + EPClsPostfix.SRC
    LS = SrcRow.L + EPClsPostfix.SRC
    AS = SrcRow.A + EPClsPostfix.SRC
    BS = SrcRow.B + EPClsPostfix.SRC


class DstIfKey(StrEnum):
    """Destination Interfaces."""

    AD = DstRow.A + EPClsPostfix.DST
    BD = DstRow.B + EPClsPostfix.DST
    FD = DstRow.F + EPClsPostfix.DST
    LD = DstRow.L + EPClsPostfix.DST
    WD = DstRow.W + EPClsPostfix.DST
    OD = DstRow.O + EPClsPostfix.DST
    PD = DstRow.P + EPClsPostfix.DST
    UD = DstRow.U + EPClsPostfix.DST


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
DESTINATION_ROW_MAP: dict[str, DstRow] = {str(row): row for row in DstRow}
DESTINATION_ROW_SET: set[DstRow] = set(DstRow)
DESTINATION_ROW_SET_AND_U: set[str] = DESTINATION_ROW_SET | {"U"}
SOURCE_ROW_MAP: dict[str, SrcRow] = {str(row): row for row in SrcRow}
SOURCE_ROW_SET: set[SrcRow] = set(SrcRow)
DST_ONLY_ROWS: tuple[DstRow, ...] = tuple(
    sorted({DstRow.F, DstRow.O, DstRow.P, DstRow.W, DstRow.U})
)
SINGLE_ONLY_ROWS = {DstRow.F, DstRow.W, DstRow.L, SrcRow.L}
SRC_ONLY_ROWS: tuple[SrcRow, ...] = tuple(sorted({SrcRow.I}))
ROWS: tuple[Row, ...] = tuple(sorted({*SrcRow, *DstRow}))
ROW_MAP: dict[str, SrcRow | DstRow] = {str(row): row for row in ROWS}
ROW_SET: set[Row] = set(ROWS)
EPC_STR_TUPLE: tuple[EPClsPostfix, EPClsPostfix] = (EPClsPostfix.DST, EPClsPostfix.SRC)
EPC_MAP: dict[str, EndPointClass] = {"s": EndPointClass.SRC, "d": EndPointClass.DST}
ALL_ROWS_STR: str = "".join(ROWS)
ROW_CLS_INDEXED: tuple[str, ...] = tuple(SrcIfKey) + tuple(DstIfKey)
ROW_CLS_INDEXED_SET: set[str] = set(ROW_CLS_INDEXED)
_UNDER_ROW_CLS_INDEXED: tuple[str, ...] = tuple("_" + row for row in ROW_CLS_INDEXED)
_UNDER_ROW_DST_INDEXED: tuple[str, ...] = tuple("_" + row + EPClsPostfix.DST for row in DstRow)
_UNDER_DST_KEY_DICT: dict[str | Row, str] = {row: "_" + row + EPClsPostfix.DST for row in DstRow}
_UNDER_SRC_KEY_DICT: dict[str | Row, str] = {row: "_" + row + EPClsPostfix.SRC for row in SrcRow}
_UNDER_KEY_DICT: dict[str | DstIfKey | SrcIfKey, str] = {
    k: ("_" + k) for k in chain(DstIfKey, SrcIfKey)
}
