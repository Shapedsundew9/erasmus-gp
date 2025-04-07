"""Connection Graph Types."""

from enum import IntEnum, StrEnum, Enum


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


class CGKey:
    """Connection Graph Key.

    CG keys are immutable and hashable.
    They are used to identify rows, interfaces, connections and endpoints in
    a CGGraphABC object.
    """

    __slots__ = ("row", "idx", "ep_cls", "connection", "_hash")

    def __init__(
        self,
        row: SrcRow | DstRow,
        idx: int = -1,
        ep_cls: EPClsPostfix | None = None,
        connection: bool = False,
    ) -> None:
        """Initialize the End Point Key."""
        self.row: SrcRow | DstRow = row
        self.ep_cls: EPClsPostfix | None = ep_cls
        self.idx: int = idx
        self.connection: bool = connection
        # NOTE: This assumes that the properties do not change.
        self._hash = hash((self.row, self.idx, self.ep_cls, self.connection))

        # Validate the End Point Key
        # If no EP class is set then it can only be a row key
        # i.e. "A" or "B" or "I" etc.
        assert (
            ep_cls is None and idx < 0 and not connection
        ) or ep_cls is not None, "Invalid End Point Key: Row"
        # If it is a connection then the EP class must be set
        # and there must be no index
        # i.e. "Asc" or "Bdc" etc.
        assert (
            connection and ep_cls is not None and idx < 0
        ) or not connection, "Invalid End Point Key: Connection"
        # If there is an index then it can only be an endpoint
        # i.e. "A000s" or "B002d" etc.
        assert (
            ep_cls is not None and idx >= 0 and not connection
        ) or idx < 0, "Invalid End Point Key: Index"

    def __eq__(self, other: object) -> bool:
        """Compare two End Point Keys."""
        if not isinstance(other, CGKey):
            return NotImplemented
        return self._hash == other._hash

    def __hash__(self) -> int:
        """Hash the End Point Key."""
        # NOTE: This assumes that the properties do not change.
        # Asserts are removed at production time.
        assert self._hash == hash(
            (self.row, self.idx, self.ep_cls, self.connection)
        ), "Hash mismatch"
        return self._hash

    def __str__(self) -> str:
        """Stringify the End Point Key."""
        # An interface index
        if self.idx < 0 and not self.connection:
            return f"{self.row}{self.ep_cls}"
        # Interface connections key
        if self.idx < 0 and self.connection and self.ep_cls is not None:
            return f"{self.row}{self.ep_cls}c"
        # An end point key
        if self.idx >= 0 and not self.connection:
            return f"{self.row}{self.idx:03d}{self.ep_cls}"
        # A row key
        if self.ep_cls is None and self.idx < 0 and not self.connection:
            return self.row
        assert False, "Invalid Connection Graph Key"


class SrcIfKeys(Enum):
    """Source interfaces."""

    IS = CGKey(row=SrcRow.I, ep_cls=EPClsPostfix.SRC)
    LS = CGKey(row=SrcRow.L, ep_cls=EPClsPostfix.SRC)
    AS = CGKey(row=SrcRow.A, ep_cls=EPClsPostfix.SRC)
    BS = CGKey(row=SrcRow.B, ep_cls=EPClsPostfix.SRC)


class DstIfKeys(Enum):
    """Destination interfaces."""

    AD = CGKey(row=DstRow.A, ep_cls=EPClsPostfix.DST)
    BD = CGKey(row=DstRow.B, ep_cls=EPClsPostfix.DST)
    FD = CGKey(row=DstRow.F, ep_cls=EPClsPostfix.DST)
    LD = CGKey(row=DstRow.L, ep_cls=EPClsPostfix.DST)
    WD = CGKey(row=DstRow.W, ep_cls=EPClsPostfix.DST)
    OD = CGKey(row=DstRow.O, ep_cls=EPClsPostfix.DST)
    PD = CGKey(row=DstRow.P, ep_cls=EPClsPostfix.DST)
    UD = CGKey(row=DstRow.U, ep_cls=EPClsPostfix.DST)


class IfKeys(Enum):
    """All interface Keys."""

    # NOTE: Enums are final and cannot be changed after creation.
    # This is a workaround to allow the use of the same keys in both
    # so some sanity is needed below.
    IS = SrcIfKeys.IS
    LS = SrcIfKeys.LS
    AS = SrcIfKeys.AS
    BS = SrcIfKeys.BS
    AD = DstIfKeys.AD
    BD = DstIfKeys.BD
    FD = DstIfKeys.FD
    LD = DstIfKeys.LD
    WD = DstIfKeys.WD
    OD = DstIfKeys.OD
    PD = DstIfKeys.PD
    UD = DstIfKeys.UD


# NOTE: This is a workaround to allow the use of the same keys in both
# source and destination interfaces.
assert set(sk for sk in SrcIfKeys) | set(dk for dk in DstIfKeys) == set(
    IfKeys
), "Source and destination interface keys do not match. Please check the keys in IfKeys."


class SrcConnKeys(Enum):
    """Source connection keys."""

    ISC = CGKey(row=SrcRow.I, ep_cls=EPClsPostfix.SRC, connection=True)
    LSC = CGKey(row=SrcRow.L, ep_cls=EPClsPostfix.SRC, connection=True)
    ASC = CGKey(row=SrcRow.A, ep_cls=EPClsPostfix.SRC, connection=True)
    BSC = CGKey(row=SrcRow.B, ep_cls=EPClsPostfix.SRC, connection=True)


class DstConnKeys(Enum):
    """Destination connection keys."""

    ADC = CGKey(row=DstRow.A, ep_cls=EPClsPostfix.DST, connection=True)
    BDC = CGKey(row=DstRow.B, ep_cls=EPClsPostfix.DST, connection=True)
    FDC = CGKey(row=DstRow.F, ep_cls=EPClsPostfix.DST, connection=True)
    LDC = CGKey(row=DstRow.L, ep_cls=EPClsPostfix.DST, connection=True)
    WDC = CGKey(row=DstRow.W, ep_cls=EPClsPostfix.DST, connection=True)
    ODC = CGKey(row=DstRow.O, ep_cls=EPClsPostfix.DST, connection=True)
    PDC = CGKey(row=DstRow.P, ep_cls=EPClsPostfix.DST, connection=True)
    UDC = CGKey(row=DstRow.U, ep_cls=EPClsPostfix.DST, connection=True)


class EndPointClass(IntEnum):
    """End Point Class."""

    SRC = True
    DST = False


class CPI(IntEnum):
    """Indices into a JSON GC Graph End Point."""

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
DESTINATION_ROW_SET_U: set[DstRow] = set(DstRow) | {DstRow.U}
SOURCE_ROWS: tuple[SrcRow, ...] = tuple(sorted(SrcRow))
SOURCE_ROW_SET: set[SrcRow] = set(SrcRow)
DST_ONLY_ROWS: tuple[DstRow, ...] = tuple(
    sorted({DstRow.F, DstRow.W, DstRow.O, DstRow.P, DstRow.U})
)
SRC_ONLY_ROWS: tuple[SrcRow, ...] = tuple(sorted({SrcRow.I}))
ROWS: tuple[Row, ...] = tuple(sorted({*SOURCE_ROWS, *DESTINATION_ROWS}))
ROW_SET: set[Row] = set(ROWS)
EP_CLS_STR_TUPLE: tuple[EPClsPostfix, EPClsPostfix] = (EPClsPostfix.DST, EPClsPostfix.SRC)
ALL_ROWS_STR: str = "".join(ROWS)
GRAPH_ORDER: str = "IFLWABOP"
ROW_CLS_INDEXED: tuple[str, ...] = tuple(f"{row}{EPClsPostfix.SRC}" for row in SOURCE_ROWS) + tuple(
    f"{row}{EPClsPostfix.DST}" for row in DESTINATION_ROWS
)


def str2epcls(ep_cls_str: str) -> EndPointClass:
    """Convert an end point class string to an end point class integer."""
    return EndPointClass.SRC if ep_cls_str == EPClsPostfix.SRC else EndPointClass.DST
