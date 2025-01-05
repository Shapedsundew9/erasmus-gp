"""Base class for GC graph objects."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pprint import pformat
from typing import Any, Callable, Generator, cast

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_class_factory import EMPTY_CONNECTIONS
from egppy.gc_graph.end_point.end_point import DstEndPointRef, EndPoint, SrcEndPointRef
from egppy.gc_graph.end_point.end_point_type import EndPointType, end_point_type
from egppy.gc_graph.end_point.types_def import types_db
from egppy.gc_graph.gc_graph_abc import GCGraphABC
from egppy.gc_graph.interface import (
    EMPTY_INTERFACE,
    INTERFACE_MAX_LENGTH,
    AnyInterface,
    MutableInterface,
    RawInterface,
    verify_interface,
)
from egppy.gc_graph.typing import (
    CPI,
    ROW_CLS_INDEXED,
    DESTINATION_ROW_SET_AND_U,
    SOURCE_ROWS,
    SOURCE_ROW_SET,
    VALID_ROW_DESTINATIONS,
    VALID_ROW_SOURCES,
    DestinationRow,
    EndPointClass,
    EPClsPostfix,
    Row,
    SourceRow,
    str2epcls
)
from egppy.storage.cache.cacheable_obj import CacheableObjMixin

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Type of the GC Graph dictionary
GCGraphDict = Mapping[str, Sequence[Sequence[Any] | MutableInterface | ConnectionsABC]]


# Sort key function
def skey(x: tuple[int, EndPointType]) -> int:
    """Return the index."""
    return x[0]


# Key to parts
def key2parts(key: str) -> tuple[Row, int, EndPointClass]:
    """Return the parts of the key."""
    lenkey = len(key)
    if lenkey == 1:
        return cast(Row, key), 0, EndPointClass.SRC
    if lenkey <= 3:
        return cast(Row, key[0]), 0, str2epcls(key[1])
    return cast(Row, key[0]), int(key[1:4]), str2epcls(key[4])


class GCGraphMixin(CacheableObjMixin):
    """Base class for GC graph objects."""

    # Must be defined by the derived class
    _TI: Callable[[RawInterface], AnyInterface]  # interface() or mutable_interface()
    _TC: type[ConnectionsABC]

    def __init__(self, gc_graph: GCGraphDict | GCGraphABC) -> None:
        """Initialize the GC graph."""
        if isinstance(gc_graph, GCGraphABC) or not gc_graph:
            self._init_from_gc_graph(gc_graph)
        elif not isinstance(tuple(gc_graph.values())[0], list):
            self._init_from_dict(gc_graph)
        else:
            self._init_from_json(gc_graph)

        if _LOG_VERIFY:
            self.verify()
        if _LOG_CONSISTENCY:
            self.consistency()
            assert self.to_json() == gc_graph, "JSON GC Graph consistency failure."
        super().__init__()

    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        raise NotImplementedError("GCGraphMixin.__getitem__ must be overridden")

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the endpoint with the given key."""
        raise NotImplementedError("GCGraphMixin.__setitem__ must be overridden")

    def _init_from_gc_graph(self, gc_graph: GCGraphABC | GCGraphDict) -> None:
        """Initialize from a GCGraphABC or empty dictionary."""
        for key in ROW_CLS_INDEXED:
            self[key] = gc_graph.get(key, EMPTY_INTERFACE)
            self[key + "c"] = gc_graph.get(key + "c", EMPTY_CONNECTIONS)

    def _init_from_dict(self, gc_graph: GCGraphDict) -> None:
        """Initialize from a dictionary with keys and values like a GCGraphABC."""
        rtype = self._TC.get_ref_iterable_type()
        for key in ROW_CLS_INDEXED:
            ckey = key + "c"
            if key not in gc_graph:
                self[key] = EMPTY_INTERFACE
                self[ckey] = EMPTY_CONNECTIONS
            elif ckey not in gc_graph:
                self[key] = gc_graph[key]
                self[ckey] = self._TC(rtype() for _ in gc_graph[key])

    def _init_from_json(self, gc_graph: GCGraphDict) -> None:
        """Initialize from a JSON formatted GC graph.
        {
            "DSTROW":[[SRCROW, IDX, [TYP, ...]],...]
            ...
        }
        """
        src_if_typs: dict[SourceRow, set[tuple[int, EndPointType]]] = {
            r: set() for r in SOURCE_ROWS
        }
        src_if_refs: dict[SourceRow, dict[int, list[DstEndPointRef]]] = {}
        for row, jeps in gc_graph.items():
            if row not in DESTINATION_ROW_SET_AND_U:
                raise ValueError(f"Invalid row in JSON GC Graph. "
                                 f"Expected a destination row but got: {row}")
            if row != "U":
                self._process_json_row(row, jeps, src_if_refs)
            self._collect_src_references(jeps, src_if_typs)

        self._create_source_interfaces(src_if_typs)
        self._add_src_references_to_destinations(src_if_refs)

    def _process_json_row(
        self,
        row: str,
        jeps: Sequence[Sequence[Any]],
        src_if_refs: dict[SourceRow, dict[int, list[DstEndPointRef]]],
    ) -> None:
        """Process a row in the JSON GC graph."""
        # Some sanity to start with
        if not isinstance(jeps, list):
            raise ValueError(f"Invalid row in JSON GC Graph. Expected a list but got: {type(jeps)}")
        if not all(isinstance(jep, list) for jep in jeps):
            typs = [type(jep) for jep in jeps]
            raise ValueError(f"Invalid row in JSON GC Graph. Expected a list[list] but got: {typs}")

        rowd = row + EPClsPostfix.DST
        self[rowd] = self._TI(jep[CPI.TYP] for jep in jeps)
        self[rowd + "c"] = self._TC(
            self._TC.get_ref_iterable_type()((SrcEndPointRef(jep[CPI.ROW], jep[CPI.IDX]),))
            for jep in jeps
        )
        for idx, jep in enumerate(jeps):
            # Some sanity on the endpoint
            if jep[CPI.ROW] not in SOURCE_ROW_SET:
                raise ValueError(f"Invalid source row in JSON GC Graph. "
                                 f"Expected a row but got: {jep[CPI.ROW]}")
            if not 0 <= jep[CPI.IDX] < INTERFACE_MAX_LENGTH:
                raise ValueError(f"Invalid index in JSON GC Graph. Expected 0 <= IDX"
                                 f" < {INTERFACE_MAX_LENGTH} but got: {jep[CPI.IDX]}")
            if not isinstance(jep[CPI.TYP], list):
                raise ValueError(f"Invalid type in JSON GC Graph. Expected a list but"
                                 f" got: {type(jep[CPI.TYP])}")
            if not all(isinstance(t, str | int) for t in jep[CPI.TYP]):
                raise ValueError(f"Invalid type in JSON GC Graph. Expected a list of str | int"
                                 f" but got: {[type(t) for t in jep[CPI.TYP]]}")

            # Collect the source row references
            src_if_refs.setdefault(jep[CPI.ROW], {}).setdefault(jep[CPI.IDX], []).append(
                DstEndPointRef(cast(DestinationRow, row), idx)
            )

    def _collect_src_references(
        self,
        jeps: Sequence[Any],
        src_if_typs: dict[SourceRow, set[tuple[int, EndPointType]]],
    ) -> None:
        """Collect references to the source interfaces."""
        for jep in jeps:
            src_if_typs[jep[CPI.ROW]].add((jep[CPI.IDX], end_point_type(jep[CPI.TYP])))

    def _create_source_interfaces(
        self, src_if_typs: dict[SourceRow, set[tuple[int, EndPointType]]]
    ) -> None:
        """Create source interfaces from collected references."""
        for row, sif in src_if_typs.items():
            self[row + EPClsPostfix.SRC] = self._TI(t for _, t in sorted(sif, key=skey))

    def _add_src_references_to_destinations(
        self, src_if_refs: dict[SourceRow, dict[int, list[DstEndPointRef]]]
    ) -> None:
        """Add references to the destinations from the sources."""
        for row, idx_refs in src_if_refs.items():
            src_refs = [self._TC.get_ref_iterable_type()()] * len(self[row + EPClsPostfix.SRC])
            for idx, refs in idx_refs.items():
                src_refs[idx] = self._TC.get_ref_iterable_type()(
                    DstEndPointRef(r.get_row(), r.get_idx()) for r in refs
                )
            self[row + EPClsPostfix.SRC + "c"] = self._TC(src_refs)

    def __contains__(self, key: object) -> bool:
        """Return True if the row, interface or endpoint exists."""
        if isinstance(key, str):
            keylen = len(key)
            if keylen == 1:  # Its a row
                return (
                    self.get(key + EPClsPostfix.DST, EMPTY_INTERFACE) is not EMPTY_INTERFACE
                    or self.get(key + EPClsPostfix.SRC, EMPTY_INTERFACE) is not EMPTY_INTERFACE
                )
            if keylen == 2:  # Its an interface
                return self.get(key, EMPTY_INTERFACE) is not EMPTY_INTERFACE
            if keylen == 3:  # Its connections
                return self.get(key, EMPTY_CONNECTIONS) is not EMPTY_CONNECTIONS
            if keylen == 5:  # Its an endpoint
                iface = self.get(key[0] + key[4], EMPTY_INTERFACE)
                return len(iface) > int(key[1:4]) + 1
        return False  # Its none of the above!

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        if not isinstance(other, GCGraphABC):
            return False
        for key in ROW_CLS_INDEXED:
            key_in_self = key in self
            if key_in_self != (key in other):
                return False
            if key_in_self and (self[key] != other[key] or self[key + "c"] != other[key + "c"]):
                return False
        return True

    def __iter__(self) -> Generator[EndPoint, None, None]:
        """Return an iterator over the GC graph end points."""
        for key in self.epkeys():
            yield self[key]

    def __repr__(self) -> str:
        """Return a string representation of the GC graph."""
        return pformat(self.to_json(), indent=4, width=120)

    def check_required_connections(self) -> list[tuple[SourceRow, DestinationRow]]:
        """Return a list of required connections that are missing."""
        retval = []
        if self.codon_or_empty():
            return retval

        if self.conditional_graph():
            # I must connect to F
            fdc: ConnectionsABC = self["Fdc"]
            if len(fdc) == 0 or len(fdc[0]) == 0 or fdc[0][0].get_row() != SourceRow.I:
                retval.append((SourceRow.I, DestinationRow.F))
            # I must connect to B
            bdc: ConnectionsABC = self["Bdc"]
            if len(bdc) == 0 or all(ep[0].get_row() != SourceRow.I for ep in bdc):
                retval.append((SourceRow.I, DestinationRow.B))
            # A must connect to O
            odc: ConnectionsABC = self["Odc"]
            if len(odc) == 0 or all(ep[0].get_row() != SourceRow.A for ep in odc):
                retval.append((SourceRow.A, DestinationRow.O))
            # B must connect to P
            pdc: ConnectionsABC = self["Pdc"]
            if len(pdc) == 0 or all(ep[0].get_row() != SourceRow.B for ep in pdc):
                retval.append((SourceRow.B, DestinationRow.P))

        if self.standard_graph():
            # B must connect to O
            odc: ConnectionsABC = self["Odc"]
            _logger.debug("Odc: %s", odc)
            if len(odc) == 0 or all(ep[0].get_row() != SourceRow.B for ep in odc):
                retval.append((SourceRow.B, DestinationRow.O))

        # In all cases I must be connected to A
        adc: ConnectionsABC = self["Adc"]
        _logger.debug("Adc: %s", adc)
        if len(adc) == 0 or all(ep[0].get_row() != SourceRow.I for ep in adc):
            retval.append((SourceRow.I, DestinationRow.A))

        return retval

    def codon_or_empty(self) -> bool:
        """Return True if the graph is a codon or empty."""
        return DestinationRow.A not in self

    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return DestinationRow.F in self

    def consistency(self) -> None:
        """Check the consistency of the GC graph."""

        if self.conditional_graph():
            fdi: AnyInterface = self[DestinationRow.F + EPClsPostfix.DST]
            assert len(fdi) == 1, f"Row F must only have one end point: {len(fdi)}"
            assert fdi[0] == types_db["bool"].ept(), f"F EP must be bool: {fdi[0]}"
            fdc: ConnectionsABC = self[DestinationRow.F + EPClsPostfix.DST + "c"]
            assert len(fdc) == 1, f"Row F must only have one connection: {len(fdc)}"
            assert fdc[0][0].get_row() == SourceRow.I, f"Row F src must be I: {fdc[0][0].get_row()}"

        if self.standard_graph() or self.conditional_graph():
            adi: AnyInterface = self[DestinationRow.A + EPClsPostfix.DST]
            assert len(adi) >= 1, f"Row A must have at least one end point: {len(adi)}"
            bdi: AnyInterface = self[DestinationRow.B + EPClsPostfix.DST]
            assert len(bdi) >= 1, f"Row B must have at least one end point: {len(bdi)}"
            asi: AnyInterface = self[SourceRow.A + EPClsPostfix.SRC]
            assert len(asi) >= 1, f"Row A must have at least one end point: {len(asi)}"
            bsi: AnyInterface = self[SourceRow.B + EPClsPostfix.SRC]
            assert len(bsi) >= 1, f"Row B must have at least one end point: {len(bsi)}"

        # All graphs
        isi: AnyInterface = self[SourceRow.I + EPClsPostfix.SRC]
        assert len(isi) >= 1, f"Row I must have at least one end point: {len(isi)}"
        odi: AnyInterface = self[DestinationRow.O + EPClsPostfix.DST]
        assert len(odi) >= 1, f"Row O must have at least one end point: {len(odi)}"

        # Check connections
        for key in ROW_CLS_INDEXED:
            iface = self.get(key, EMPTY_INTERFACE)
            conns = self.get(key + "c", EMPTY_CONNECTIONS)
            conns.consistency()
            assert len(iface) == len(conns), f"Length mismatch: {len(iface)} != {len(conns)}"

            # Check desintation connections
            if key[1] == EPClsPostfix.DST:
                for idx, refs in enumerate(conns):
                    assert len(refs) == 1, f"Dst EPs must have one reference: {len(refs)}"
                    srow = refs[0].get_row()
                    assert (
                        srow in VALID_ROW_SOURCES[self.conditional_graph()]
                    ), f"Invalid src row: {srow}"
                    styp = self[srow + EPClsPostfix.SRC][refs[0].get_idx()]
                    assert iface[idx] == styp, f"Dst EP type mismatch: {iface[idx]} != {styp}"
                    srefs = self[srow + EPClsPostfix.SRC + "c"][refs[0].get_idx()]
                    assert (
                        DstEndPointRef(cast(Row, key[0]), idx) in srefs
                    ), f"Src not connected to Dst: {key[0]}[{idx}]"
            else:
                # Check source connections
                for idx, refs in enumerate(conns):
                    for ref in refs:
                        drow = ref.get_row()
                        assert (
                            drow in VALID_ROW_DESTINATIONS[self.conditional_graph()]
                        ), f"Invalid dst row: {drow}"
                        dtyp = self[drow + EPClsPostfix.DST][ref.get_idx()]
                        assert iface[idx] == dtyp, f"Src typ mismatch: {iface[idx]} != {dtyp}"
                        drefs = self[drow + EPClsPostfix.DST + "c"][ref.get_idx()]
                        assert (
                            SrcEndPointRef(cast(Row, key[0]), idx) in drefs
                        ), f"Dst not connected to src: {key[0]}[{idx}]"

        super().consistency()

    def epkeys(self) -> Generator[str, None, None]:
        """Return an iterator over the GC graph endpoint keys."""
        for key in self.ikeys():
            for idx in range(len(self[key])):
                yield f"{key[0]}{idx:03d}{key[1]}"

    def get(self, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key."""
        try:
            return self[key]
        except KeyError:
            return default

    def ikeys(self) -> Generator[str, None, None]:
        """Return an iterator over the GC graph interface keys."""
        for key in (r for r in ROW_CLS_INDEXED if r in self):
            yield key

    def itypes(self) -> tuple[list[EndPointType], list[int]]:
        """Return the input types and input row indices into them."""
        ikey = SourceRow.I + EPClsPostfix.SRC
        itypes = list(self.types(ikey))
        ilu = {t: i for i, t in enumerate(itypes)}
        return itypes, [ilu[i] for i in self.get(ikey, EMPTY_INTERFACE)]

    def otypes(self) -> tuple[list[EndPointType], list[int]]:
        """Return the output types and output row indices into them."""
        okey = DestinationRow.O + EPClsPostfix.DST
        otypes = list(self.types(okey))
        olu = {t: o for o, t in enumerate(otypes)}
        return otypes, [olu[i] for i in self.get(okey, EMPTY_INTERFACE)]

    def setdefault(self, key: str, default: Any) -> Any:
        """Set the endpoint with the given key to the default if it does not exist."""
        if key not in self:
            self[key] = default
        return self[key]

    def to_json(self) -> dict[str, Any]:
        """Return a JSON GC Graph."""
        jgcg: dict[str, list[list[Any]]] = {}
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.DST and k in self):
            iface: AnyInterface = self[key]
            conns: ConnectionsABC = self[key + "c"]
            jgcg[key[0]] = [
                [str(r[0].get_row()), r[0].get_idx(), [td.uid for td in ept]]
                for r, ept in zip(conns, iface, strict=True)
            ]
        ucn: list[list[Any]] = []
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.SRC and k in self):
            iface: AnyInterface = self[key]
            conns: ConnectionsABC = self[key + "c"]
            row = cast(Row, key[0])
            ucn.extend(
                [
                    [row, i, [td.uid for td in ept]]
                    for i, (r, ept) in enumerate(zip(conns, iface, strict=True))
                    if not r
                ]
            )
        if ucn:
            jgcg["U"] = sorted(ucn, key=lambda x: x[0] + f"{x[1]:03d}")
        return jgcg

    def standard_graph(self) -> bool:
        """Return True if the graph is a standard graph."""
        return DestinationRow.F not in self and DestinationRow.A in self

    def types(self, ikey: str) -> Generator[EndPointType, None, None]:
        """Return an iterator over the ordered interface endpoint types.
        Endpoint types are returned in the order of lowest value to highest.
        """
        return (typ for typ in sorted({typ for typ in self.get(ikey, EMPTY_INTERFACE)}))

    def valid_srcs(self, row: DestinationRow, typ: EndPointType) -> list[tuple[SourceRow, int]]:
        """Return a list of valid source row endpoint indexes."""
        srows = VALID_ROW_SOURCES[DestinationRow.F in self][row]
        return [(srow, sidx) for srow in srows for sidx in self[srow + EPClsPostfix.SRC].find(typ)]

    def verify(self) -> None:
        """Verify the GC graph."""
        key = "Null"
        try:
            for key in ROW_CLS_INDEXED:
                verify_interface(self.get(key, EMPTY_INTERFACE))
            super().verify()
        except AssertionError as e:
            _logger.error("Interface %s verification failed", key)
            raise AssertionError(f"GC Graph verification failed: {e} for graph\n{self}") from e
