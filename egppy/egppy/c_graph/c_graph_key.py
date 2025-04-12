"""Connection Graph Types."""

from enum import IntEnum, StrEnum
from collections.abc import Sized, Iterator, Iterable


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


class CGraphKey(Sized):
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
        if not isinstance(other, CGraphKey):
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

    def __len__(self) -> int:
        """Return the length of the End Point Key."""
        # A row or interface key
        if self.idx < 0 and not self.connection:
            return 1 if self.ep_cls is None else 2
        # Interface connections key
        if self.connection and self.ep_cls is not None:
            return 3
        # An end point key
        if self.idx >= 0:
            assert not self.connection, "Invalid Connection Graph Key"
            return 5
        assert False, "Invalid Connection Graph Key"

    def __str__(self) -> str:
        """Stringify the End Point Key."""
        # A row key or interface key
        if self.ep_cls is None and not self.connection:
            assert self.idx < 0, "Invalid Connection Graph Key"
            return self.row if self.ep_cls is None else f"{self.row}{self.ep_cls}"
        # Interface connections key
        if self.connection and self.ep_cls is not None:
            assert self.idx < 0, "Invalid Connection Graph Key"
            return f"{self.row}{self.ep_cls}c"
        # An end point key
        if self.idx >= 0:
            assert not self.connection, "Invalid Connection Graph Key"
            return f"{self.row}{self.idx:03d}{self.ep_cls}"
        assert False, "Invalid Connection Graph Key"


class _SrcIfKeys(Iterable[CGraphKey]):
    """Source interfaces."""

    IS = CGraphKey(row=SrcRow.I, ep_cls=EPClsPostfix.SRC)
    LS = CGraphKey(row=SrcRow.L, ep_cls=EPClsPostfix.SRC)
    AS = CGraphKey(row=SrcRow.A, ep_cls=EPClsPostfix.SRC)
    BS = CGraphKey(row=SrcRow.B, ep_cls=EPClsPostfix.SRC)

    def __iter__(self) -> Iterator[CGraphKey]:
        """Iterate over the source interface keys."""
        for key in (_SrcIfKeys.IS, _SrcIfKeys.LS, _SrcIfKeys.AS, _SrcIfKeys.BS):
            yield key


SrcIFKeys = _SrcIfKeys()


class _DstIfKeys(Iterable[CGraphKey]):
    """Destination interfaces."""

    AD = CGraphKey(row=DstRow.A, ep_cls=EPClsPostfix.DST)
    BD = CGraphKey(row=DstRow.B, ep_cls=EPClsPostfix.DST)
    FD = CGraphKey(row=DstRow.F, ep_cls=EPClsPostfix.DST)
    LD = CGraphKey(row=DstRow.L, ep_cls=EPClsPostfix.DST)
    WD = CGraphKey(row=DstRow.W, ep_cls=EPClsPostfix.DST)
    OD = CGraphKey(row=DstRow.O, ep_cls=EPClsPostfix.DST)
    PD = CGraphKey(row=DstRow.P, ep_cls=EPClsPostfix.DST)
    UD = CGraphKey(row=DstRow.U, ep_cls=EPClsPostfix.DST)

    def __iter__(self) -> Iterator[CGraphKey]:
        """Iterate over the destination interface keys."""
        for key in (
            _DstIfKeys.AD,
            _DstIfKeys.BD,
            _DstIfKeys.FD,
            _DstIfKeys.LD,
            _DstIfKeys.WD,
            _DstIfKeys.OD,
            _DstIfKeys.PD,
            _DstIfKeys.UD,
        ):
            yield key


DstIfKeys = _DstIfKeys()


class _IfKeys(Iterable[CGraphKey]):
    """All interface Keys."""

    def __iter__(self) -> Iterator[CGraphKey]:
        """Iterate over all interface keys."""
        yield from SrcIFKeys.__iter__()
        yield from DstIfKeys.__iter__()


IfKeys = _IfKeys()


class _SrcConnKeys(Iterable[CGraphKey]):
    """Source connection keys."""

    ISC = CGraphKey(row=SrcRow.I, ep_cls=EPClsPostfix.SRC, connection=True)
    LSC = CGraphKey(row=SrcRow.L, ep_cls=EPClsPostfix.SRC, connection=True)
    ASC = CGraphKey(row=SrcRow.A, ep_cls=EPClsPostfix.SRC, connection=True)
    BSC = CGraphKey(row=SrcRow.B, ep_cls=EPClsPostfix.SRC, connection=True)

    def __iter__(self) -> Iterator[CGraphKey]:
        """Iterate over the source connection keys."""
        for key in (_SrcConnKeys.ISC, _SrcConnKeys.LSC, _SrcConnKeys.ASC, _SrcConnKeys.BSC):
            yield key


SrcConnKeys = _SrcConnKeys()


class _DstConnKeys(Iterable[CGraphKey]):
    """Destination connection keys."""

    ADC = CGraphKey(row=DstRow.A, ep_cls=EPClsPostfix.DST, connection=True)
    BDC = CGraphKey(row=DstRow.B, ep_cls=EPClsPostfix.DST, connection=True)
    FDC = CGraphKey(row=DstRow.F, ep_cls=EPClsPostfix.DST, connection=True)
    LDC = CGraphKey(row=DstRow.L, ep_cls=EPClsPostfix.DST, connection=True)
    WDC = CGraphKey(row=DstRow.W, ep_cls=EPClsPostfix.DST, connection=True)
    ODC = CGraphKey(row=DstRow.O, ep_cls=EPClsPostfix.DST, connection=True)
    PDC = CGraphKey(row=DstRow.P, ep_cls=EPClsPostfix.DST, connection=True)
    UDC = CGraphKey(row=DstRow.U, ep_cls=EPClsPostfix.DST, connection=True)

    def __iter__(self) -> Iterator[CGraphKey]:
        """Iterate over the destination connection keys."""
        for key in (
            _DstConnKeys.ADC,
            _DstConnKeys.BDC,
            _DstConnKeys.FDC,
            _DstConnKeys.LDC,
            _DstConnKeys.WDC,
            _DstConnKeys.ODC,
            _DstConnKeys.PDC,
            _DstConnKeys.UDC,
        ):
            yield key


DstConnKeys = _DstConnKeys()


class _ConnKeys(Iterable[CGraphKey]):
    """All connection keys."""

    def __iter__(self) -> Iterator[CGraphKey]:
        """Iterate over all connection keys."""
        yield from SrcConnKeys.__iter__()
        yield from DstConnKeys.__iter__()


ConnKeys = _ConnKeys()


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


def str2epcls(ep_cls_str: str) -> EndPointClass:
    """Convert an end point class string to an end point class integer."""
    return EndPointClass.SRC if ep_cls_str == EPClsPostfix.SRC else EndPointClass.DST
