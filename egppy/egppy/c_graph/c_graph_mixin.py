"""Base class for Connection Graph objects."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pprint import pformat
from typing import Any, Callable, Generator, Iterable

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.c_graph_validation import (
    valid_jcg,
    CGT_VALID_SRC_ROWS,
)
from egppy.c_graph.connections.connections_abc import ConnectionsABC
from egppy.c_graph.connections.connections_class_factory import NULL_CONNECTIONS
from egppy.c_graph.end_point.end_point import DstEndPointRef, EndPoint, SrcEndPointRef
from egppy.c_graph.end_point.end_point_type import EndPointType, ept_to_str, str_to_ept, TypesDef
from egppy.c_graph.c_graph_abc import CGraphABC
from egppy.c_graph.c_graph_type import CGraphType, c_graph_type
from egppy.c_graph.interface import (
    NULL_INTERFACE,
    AnyInterface,
    MutableInterface,
    RawInterface,
    interface_to_types_idx,
    verify_interface,
)
from egppy.c_graph.c_graph_constants import (
    CPI,
    ROW_CLS_INDEXED,
    ROW_MAP,
    SOURCE_ROWS,
    DstRow,
    EndPointClass,
    EPClsPostfix,
    Row,
    SrcRow,
    EPC_MAP,
    JSONCGraph,
    JSONRefRow,
    EMPTY_JSON_CGRAPH,
)
from egppy.storage.cache.cacheable_obj import CacheableObjMixin

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Type of the Connection Graph dictionary
CGraphDict = Mapping[str, Sequence[Sequence[Any] | MutableInterface | ConnectionsABC]]


# Sort key function
def skey(x: tuple[int, EndPointType]) -> int:
    """Return the index."""
    return x[0]


# Key to parts
def key2parts(key: str) -> tuple[Row, int, EndPointClass]:
    """Return the parts of the key.
    <row>
    <row><class>
    <row><index><class>
    """
    lenkey = len(key)
    if lenkey == 1:
        return ROW_MAP[key], 0, EndPointClass.SRC
    if lenkey <= 3:
        return ROW_MAP[key[0]], 0, EPC_MAP[key[1]]
    return ROW_MAP[key[0]], int(key[1:4]), EPC_MAP[key[4]]


class CGraphMixin(CacheableObjMixin):
    """Base class for Connection Graph objects."""

    # Must be defined by the derived class
    _TI: Callable[[RawInterface], AnyInterface]  # interface() or mutable_interface()
    _TC: type[ConnectionsABC]

    def __init__(self, c_graph: JSONCGraph | CGraphDict | CGraphABC) -> None:
        """Initialize the Connection Graph."""
        if isinstance(c_graph, CGraphABC):
            self._init_from_c_graph(c_graph)
        elif c_graph and not isinstance(tuple(c_graph.values())[0], list):
            # FIXME: Not sure why this exists
            assert isinstance(tuple(c_graph.values())[0], list), "Using this path."
            self._init_from_dict(c_graph)
        else:
            assert isinstance(c_graph, dict), "Invalid Connection Graph type."
            self._init_from_json(c_graph if c_graph else EMPTY_JSON_CGRAPH)  # type: ignore

        if _LOG_VERIFY:
            self.verify()
        if _LOG_CONSISTENCY:
            self.consistency()
            assert self.to_json() == c_graph, "JSON Connection Graph consistency failure."
        super().__init__()

    def _init_from_c_graph(self, c_graph: CGraphABC | CGraphDict) -> None:
        """Initialize from a CGraphABC or empty dictionary."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        for key in ROW_CLS_INDEXED:
            self[key] = c_graph.get(key, NULL_INTERFACE)
            self[key + "c"] = c_graph.get(key + "c", NULL_CONNECTIONS)

    def _init_from_dict(self, c_graph: CGraphDict | dict) -> None:
        """Initialize from a dictionary with keys and values like a CGraphABC."""
        assert isinstance(self, dict), "Invalid Connection Graph type."
        rtype = self._TC.get_ref_iterable_type()
        for key in ROW_CLS_INDEXED:
            ckey = key + "c"
            if key not in c_graph:
                self[key] = NULL_INTERFACE
                self[ckey] = NULL_CONNECTIONS
            elif ckey not in c_graph:
                self[key] = c_graph[key]
                self[ckey] = self._TC(rtype() for _ in c_graph[key])

    def _init_from_json(self, c_graph: JSONCGraph) -> None:
        """Initialize from a JSON formatted Connection Graph.
        {
            "DSTROW":[[SRCROW, IDX, [TYP, ...]],...]
            ...
        }
        """
        src_if_typs: dict[SrcRow, set[tuple[int, EndPointType]]] = {}
        src_if_refs: dict[SrcRow, dict[int, list[DstEndPointRef]]] = {}
        if _LOG_DEBUG:
            valid_jcg(c_graph)
        for row, jeps in c_graph.items():
            self._process_json_row(row, jeps, src_if_refs)
            self._collect_src_references(jeps, src_if_typs)

        self._create_source_interfaces(src_if_typs)
        self._add_src_references_to_destinations(src_if_refs)

    def _process_json_row(
        self,
        row: DstRow,
        jeps: JSONRefRow,
        src_if_refs: dict[SrcRow, dict[int, list[DstEndPointRef]]],
    ) -> None:
        """Process a row in the JSON Connection Graph."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        rowd = row + EPClsPostfix.DST
        iface: list[tuple[TypesDef, ...]] = []
        conns: list[Iterable[SrcEndPointRef]] = []
        rit: type = self._TC.get_ref_iterable_type()
        for idx, jep in enumerate(jeps):
            # Extra the data from the JSON reference
            _row = jep[CPI.ROW]
            _idx = jep[CPI.IDX]
            _typ = jep[CPI.TYP]

            # Fix the types
            assert isinstance(_row, str), f"Invalid row: {_row}"
            assert isinstance(_idx, int), f"Invalid index: {_idx}"
            assert isinstance(_typ, str), f"Invalid type: {_typ}"
            src_row = SrcRow(_row)
            # Build the interface and connections

            iface.append(str_to_ept(_typ))
            conns.append(rit((SrcEndPointRef(src_row, _idx),)))

            # Collect the source row references
            src_if_refs.setdefault(src_row, {}).setdefault(_idx, []).append(
                DstEndPointRef(row, idx)
            )
        self[rowd] = self._TI(iface)
        self[rowd + "c"] = self._TC(conns)

    def _collect_src_references(
        self,
        jeps: Sequence[Any],
        src_if_typs: dict[SrcRow, set[tuple[int, EndPointType]]],
    ) -> None:
        """Collect references to the source interfaces."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        for jep in jeps:
            src_if_typs.setdefault(jep[CPI.ROW], set()).add(
                (jep[CPI.IDX], str_to_ept(jep[CPI.TYP]))
            )

    def _create_source_interfaces(
        self, src_if_typs: dict[SrcRow, set[tuple[int, EndPointType]]]
    ) -> None:
        """Create source interfaces from collected references."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        # It is important to create empty interfaces for mutable graphs
        for row, sif in src_if_typs.items():
            self[row + EPClsPostfix.SRC] = self._TI(t for _, t in sorted(sif, key=skey))

    def _add_src_references_to_destinations(
        self, src_if_refs: dict[SrcRow, dict[int, list[DstEndPointRef]]]
    ) -> None:
        """Add references to the destinations from the sources."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        for row, idx_refs in src_if_refs.items():
            src_refs = [self._TC.get_ref_iterable_type()()] * len(self[row + EPClsPostfix.SRC])
            for idx, refs in idx_refs.items():
                src_refs[idx] = self._TC.get_ref_iterable_type()(
                    DstEndPointRef(r.get_row(), r.get_idx()) for r in refs
                )
            self[row + EPClsPostfix.SRC + "c"] = self._TC(src_refs)

    def __contains__(self, key: str) -> bool:
        """Return True if the row, interface or endpoint exists."""
        if isinstance(key, str):
            keylen = len(key)
            if keylen == 1:  # Its a row
                return (
                    self.get(key + EPClsPostfix.DST, NULL_INTERFACE) is not NULL_INTERFACE
                    or self.get(key + EPClsPostfix.SRC, NULL_INTERFACE) is not NULL_INTERFACE
                )
            if keylen == 2:  # Its an interface
                return self.get(key, NULL_INTERFACE) is not NULL_INTERFACE
            if keylen == 3:  # Its connections
                return self.get(key, NULL_CONNECTIONS) is not NULL_CONNECTIONS
            if keylen == 5:  # Its an endpoint
                iface = self.get(key[0] + key[4], NULL_INTERFACE)
                return len(iface) > int(key[1:4])
        return False  # Its none of the above!

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        if not isinstance(other, CGraphABC):
            return False
        for key in ROW_CLS_INDEXED:
            key_in_self = key in self
            if key_in_self != (key in other):
                return False
            if key_in_self and (self[key] != other[key] or self[key + "c"] != other[key + "c"]):
                return False
        return True

    def __hash__(self) -> int:
        # """Return the hash of the Connection Graph."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        return hash(hash(c) for c in self)

    def __iter__(self) -> Generator[EndPoint, None, None]:
        """Return an iterator over the Connection Graph end points."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        for key in self.epkeys():
            yield self[key]

    def __repr__(self) -> str:
        """Return a string representation of the Connection Graph."""
        return pformat(self.to_json(), indent=4, width=120)

    def check_required_connections(self) -> list[tuple[SrcRow, DstRow]]:
        """Return a list of required connections that are missing."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        cgt: CGraphType = c_graph_type(self)
        if cgt == CGraphType.IF_THEN or cgt == CGraphType.IF_THEN_ELSE:
            # Interface Fd[0] must be connected to row I
            return [(SrcRow.I, DstRow.F)] if not self["Fdc"][0] else []
        if cgt == CGraphType.FOR_LOOP:
            # Interface Ld[0] must be connected to row I
            return [(SrcRow.I, DstRow.L)] if not self["Ldc"][0] else []
        if cgt == CGraphType.WHILE_LOOP:
            # Interface Ld[0] must be connected to row I
            retval = [(SrcRow.I, DstRow.L)] if not self["Ldc"][0] else []
            # Interface Wd[0] must be connected to row A
            if not self["Wdc"][0]:
                retval.append((SrcRow.A, DstRow.W))
        # No required connections are missing
        return []

    def consistency(self) -> None:
        """Check the consistency of the Connection Graph."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        # cgt: CGraphType = c_graph_type(self)
        # TODO: Implement this function
        super().consistency()

    def epkeys(self) -> Generator[str, None, None]:
        """Return an iterator over the Connection Graph endpoint keys."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        for key in self.ikeys():
            for idx in range(len(self[key])):
                yield f"{key[0]}{idx:03d}{key[1]}"

    def get(self, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        try:
            return self[key]
        except KeyError:
            return default

    def ikeys(self) -> Generator[str, None, None]:
        """Return an iterator over the Connection Graph interface keys."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        for key in (r for r in ROW_CLS_INDEXED if r in self):
            yield key

    def itypes(self) -> tuple[tuple[tuple[int, ...], ...], bytes]:
        """Return the input types and input row indices into them."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        ikey = SrcRow.I + EPClsPostfix.SRC
        return interface_to_types_idx(self.get(ikey, NULL_INTERFACE))

    def otypes(self) -> tuple[tuple[tuple[int, ...], ...], bytes]:
        """Return the output types and output row indices into them."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        okey = DstRow.O + EPClsPostfix.DST
        return interface_to_types_idx(self.get(okey, NULL_INTERFACE))

    def setdefault(self, key: str, default: Any) -> Any:
        """Set the endpoint with the given key to the default if it does not exist."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        if key not in self:
            self[key] = default
        return self[key]

    def to_json(self) -> dict[str, Any]:
        """Return a JSON Connection Graph."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        jgcg: dict[str, list[list[Any]]] = {dr: [] for dr in CGT_VALID_SRC_ROWS[c_graph_type(self)]}
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.DST and k in self):
            iface: AnyInterface = self[key]
            conns: ConnectionsABC = self[key + "c"]
            jgcg[key[0]] = [
                [str(r[0].get_row()), r[0].get_idx(), ept_to_str(ept)]
                for r, ept in zip(conns, iface, strict=True)
            ]
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.SRC and k in self):
            iface: AnyInterface = self[key]
            conns: ConnectionsABC = self[key + "c"]
            row = ROW_MAP[key[0]]
            jgcg[DstRow.U].extend(
                [
                    [row, i, ept_to_str(ept)]
                    for i, (r, ept) in enumerate(zip(conns, iface, strict=True))
                    if not r
                ]
            )
        jgcg[DstRow.U].sort(key=lambda x: x[0] + f"{x[1]:03d}")
        return jgcg

    def type(self) -> CGraphType:
        """Return the types of the Connection Graph."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        return c_graph_type(self)

    def valid_srcs(self, row: DstRow, typ: EndPointType) -> list[tuple[SrcRow, int]]:
        """Return a list of valid source row endpoint indexes."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        srows: frozenset[SrcRow] = CGT_VALID_SRC_ROWS[c_graph_type(self)][row]
        return [(srow, sidx) for srow in srows for sidx in self[srow + EPClsPostfix.SRC].find(typ)]

    def verify(self) -> None:
        """Verify the Connection Graph."""
        assert isinstance(self, CGraphABC), "Invalid Connection Graph type."
        key = "Null"
        try:
            for key in ROW_CLS_INDEXED:
                verify_interface(self.get(key, NULL_INTERFACE))
            super().verify()
        except AssertionError as e:
            _logger.error("Interface %s verification failed", key)
            raise AssertionError(
                f"Connection Graph verification failed: {e} for graph\n{self}"
            ) from e
