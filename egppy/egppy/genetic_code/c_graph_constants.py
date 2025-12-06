"""Common Erasmus GP Types."""

from enum import IntEnum, StrEnum
from itertools import chain


class SrcRow(StrEnum):
    """Source rows.
    IMPORTANT: This order is mandated to preserve signature compatibility.
    See CGraph.py CGraph.to_json() for more details.
    """

    I = "I"
    L = "L"
    S = "S"
    W = "W"
    A = "A"
    B = "B"


class DstRow(StrEnum):
    """Destination rows.
    IMPORTANT: This order is mandated to preserve signature compatibility.
    See CGraph.py CGraph.to_json() for more details.
    """

    F = "F"
    L = "L"
    S = "S"
    T = "T"
    W = "W"
    X = "X"
    A = "A"
    B = "B"
    O = "O"
    P = "P"
    U = "U"


class EPClsPostfix(StrEnum):
    """End Point Class postfixes."""

    SRC = "s"
    DST = "d"


class SrcIfKey(StrEnum):
    """Source Interfaces.
    Whilst the order here is not critical, it is kept consistent with
    the other enums for clarity.
    """

    IS = SrcRow.I + EPClsPostfix.SRC
    LS = SrcRow.L + EPClsPostfix.SRC
    SS = SrcRow.S + EPClsPostfix.SRC
    WS = SrcRow.W + EPClsPostfix.SRC
    AS = SrcRow.A + EPClsPostfix.SRC
    BS = SrcRow.B + EPClsPostfix.SRC


class DstIfKey(StrEnum):
    """Destination Interfaces.
    Whilst the order here is not critical, it is kept consistent with
    the other enums for clarity.
    """

    FD = DstRow.F + EPClsPostfix.DST
    LD = DstRow.L + EPClsPostfix.DST
    SD = DstRow.S + EPClsPostfix.DST
    TD = DstRow.T + EPClsPostfix.DST
    WD = DstRow.W + EPClsPostfix.DST
    XD = DstRow.X + EPClsPostfix.DST
    AD = DstRow.A + EPClsPostfix.DST
    BD = DstRow.B + EPClsPostfix.DST
    OD = DstRow.O + EPClsPostfix.DST
    PD = DstRow.P + EPClsPostfix.DST
    UD = DstRow.U + EPClsPostfix.DST


# The superset
IfKey = SrcIfKey | DstIfKey


# Sanity
assert len(SrcIfKey) == len(SrcRow), "Mismatch between SrcIfKey and SrcRow lengths"
assert len(DstIfKey) == len(DstRow), "Mismatch between DstIfKey and DstRow lengths"


class EPCls(IntEnum):
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
    sorted({DstRow.F, DstRow.T, DstRow.X, DstRow.O, DstRow.P, DstRow.U})
)
SINGLE_ONLY_ROWS = {DstRow.F, DstRow.W, DstRow.L, SrcRow.L, SrcRow.W}
SINGLE_CLS_INDEXED_SET: set[DstIfKey | SrcIfKey] = {
    DstIfKey.FD,
    DstIfKey.LD,
    DstIfKey.WD,
    SrcIfKey.LS,
    SrcIfKey.WS,
}
SRC_ONLY_ROWS: tuple[SrcRow, ...] = tuple(sorted({SrcRow.I}))
ROWS: tuple[Row, ...] = tuple(sorted({*SrcRow, *DstRow}))
ROW_MAP: dict[str, SrcRow | DstRow] = {str(row): row for row in ROWS}
ROW_SET: set[Row] = set(ROWS)
EPC_STR_TUPLE: tuple[EPClsPostfix, EPClsPostfix] = (EPClsPostfix.DST, EPClsPostfix.SRC)
EPC_MAP: dict[str, EPCls] = {"s": EPCls.SRC, "d": EPCls.DST}
ALL_ROWS_STR: str = "".join(ROWS)
IMPLY_P_ROWS: set[DstRow] = {DstRow.F, DstRow.L, DstRow.S, DstRow.W}
IMPLY_P_IFKEYS: set[DstIfKey] = {DstIfKey.FD, DstIfKey.LD, DstIfKey.SD, DstIfKey.WD}
ROW_CLS_INDEXED_ORDERED: tuple[IfKey, ...] = tuple(SrcIfKey) + tuple(DstIfKey)
ROW_CLS_INDEXED_SET: set[str] = set(ROW_CLS_INDEXED_ORDERED)
_UNDER_ROW_CLS_INDEXED: tuple[str, ...] = tuple("_" + row for row in ROW_CLS_INDEXED_ORDERED)
_UNDER_ROW_DST_INDEXED: tuple[str, ...] = tuple("_" + row + EPClsPostfix.DST for row in DstRow)
_UNDER_DST_KEY_DICT: dict[str | Row, str] = {row: "_" + row + EPClsPostfix.DST for row in DstRow}
_UNDER_SRC_KEY_DICT: dict[str | Row, str] = {row: "_" + row + EPClsPostfix.SRC for row in SrcRow}
_UNDER_KEY_DICT: dict[str | DstIfKey | SrcIfKey, str] = {
    k: ("_" + k) for k in chain(DstIfKey, SrcIfKey)
}
