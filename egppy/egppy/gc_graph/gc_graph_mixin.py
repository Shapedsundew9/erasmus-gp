"""Base class for GC graph objects."""

from __future__ import annotations

from typing import Any, Generator, Protocol, cast

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_class_factory import EMPTY_CONNECTIONS
from egppy.gc_graph.end_point.end_point import DstEndPointRef, EndPoint, SrcEndPointRef
from egppy.gc_graph.ep_type import ep_type_lookup
from egppy.gc_graph.gc_graph_abc import GCGraphABC
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.interface.interface_class_factory import EMPTY_INTERFACE
from egppy.gc_graph.typing import (
    CPI,
    ROW_CLS_INDEXED,
    SOURCE_ROWS,
    VALID_ROW_DESTINATIONS,
    VALID_ROW_SOURCES,
    DestinationRow,
    EndPointClass,
    EndPointType,
    EPClsPostfix,
    Row,
    SourceRow,
    str2epcls,
)
from egppy.storage.cache.cacheable_obj import CacheableObjMixin
from egppy.storage.cache.cacheable_obj_mixin import CacheableObjProtocol

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Sort key function
def skey(x: tuple[int, EndPointType]) -> EndPointType:
    """Return the second element of tuple."""
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


class GCGraphProtocol(CacheableObjProtocol, Protocol):
    """Genetic Code Graph Protocol."""

    def __contains__(self, key: str) -> bool:
        """Return True if the endpoint exists."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""

    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        ...  # pylint: disable=unnecessary-ellipsis

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the endpoint with the given key to the given value."""

    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        ...  # pylint: disable=unnecessary-ellipsis

    def get(self, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key."""
        ...  # pylint: disable=unnecessary-ellipsis

    def epkeys(self) -> Generator[str, None, None]:
        """Return an iterator over the GC graph endpoint keys."""
        ...  # pylint: disable=unnecessary-ellipsis

    def ikeys(self) -> Generator[str, None, None]:
        """Return an iterator over the GC graph interface keys."""
        ...  # pylint: disable=unnecessary-ellipsis

    def itypes(self: GCGraphProtocol) -> tuple[list[EndPointType], list[int]]:
        """Return the input types and input row indices into them."""
        ...  # pylint: disable=unnecessary-ellipsis

    def otypes(self: GCGraphProtocol) -> tuple[list[EndPointType], list[int]]:
        """Return the output types and output row indices into them."""
        ...  # pylint: disable=unnecessary-ellipsis

    def to_json(self) -> dict[str, Any]:
        """Return a JSON GC Graph."""
        ...  # pylint: disable=unnecessary-ellipsis

    def types(self, ikey: str) -> Generator[EndPointType, None, None]:
        """Return an iterator over the ordered interface endpoint types."""
        ...  # pylint: disable=unnecessary-ellipsis


class GCGraphMixin(CacheableObjMixin):
    """Base class for GC graph objects."""

    def __init__(self: GCGraphProtocol, gc_graph: dict[str, list[list[Any]]] | GCGraphABC) -> None:
        """Initialize the GC graph."""
        # Step through the json_gc_graph and create the interfaces and connections
        if isinstance(gc_graph, GCGraphABC):
            # Copy the interfaces and connections from the given graph
            for key in ROW_CLS_INDEXED:
                self[key] = gc_graph.get(key, EMPTY_INTERFACE)
                self[key + "c"] = gc_graph.get(key + "c", EMPTY_CONNECTIONS)
        else:
            src_if_typs: dict[SourceRow, set[tuple]] = {r: set() for r in SOURCE_ROWS}
            src_if_refs: dict[SourceRow, dict[int, list[tuple]]] = {r: {} for r in SOURCE_ROWS}
            for row, jeps in gc_graph.items():
                # Row U only exists in the JSON GC Graph to identify unconnected src endpoints
                # Otherwise it is a valid destination row
                if row != "U":
                    rowd = row + EPClsPostfix.DST
                    self[rowd] = [jep[CPI.TYP] for jep in jeps]
                    self[rowd + "c"] = (
                        (SrcEndPointRef(jep[CPI.ROW], jep[CPI.IDX]),) for jep in jeps
                    )
                    # Convert each dst endpoint into a dst reference for a src endpoint
                    for idx, jep in enumerate(jeps):
                        src_if_refs[jep[CPI.ROW]].setdefault(jep[CPI.IDX], []).append((row, idx))
                # Collect the references to the source interfaces
                for jep in jeps:
                    src_if_typs[jep[CPI.ROW]].add((jep[CPI.IDX], jep[CPI.TYP]))

            # Create the source interfaces from the references collected above
            for row, sif in src_if_typs.items():
                self[row + EPClsPostfix.SRC] = (t for _, t in sorted(sif, key=skey))
            # Add the references to the destinations from the sources
            for row, idx_refs in src_if_refs.items():
                src_refs = [tuple()] * len(self[row + EPClsPostfix.SRC])
                for idx, refs in idx_refs.items():
                    src_refs[idx] = tuple(DstEndPointRef(r[0], r[1]) for r in refs)
                self[row + EPClsPostfix.SRC + "c"] = src_refs

        if _LOG_VERIFY:
            self.verify()
        if _LOG_CONSISTENCY:
            self.consistency()
            assert self.to_json() == gc_graph, "JSON GC Graph consistency failure."
        super().__init__()

    def __contains__(self: GCGraphProtocol, key: object) -> bool:
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

    def __iter__(self: GCGraphProtocol) -> Generator[EndPoint, None, None]:
        """Return an iterator over the GC graph end points."""
        for key in self.epkeys():
            yield self[key]

    def conditional_graph(self: GCGraphProtocol) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return "F" in self

    def consistency(self: GCGraphProtocol) -> None:
        """Check the consistency of the GC graph."""
        has_f = self.conditional_graph()
        # Check graph structure
        if has_f:
            fi: InterfaceABC = self["F" + EPClsPostfix.DST]
            assert len(fi) == 1, f"Row F must only have one end point: {len(fi)}"
            assert fi[0] == ep_type_lookup["n2v"]["bool"], f"F EP must be bool: {fi[0]}"
            fc: ConnectionsABC = self["F" + EPClsPostfix.DST + "c"]
            assert len(fc) == 1, f"Row F must only have one connection: {len(fc)}"
            assert fc[0][0].get_row() == SourceRow.I, f"Row F src must be I: {fc[0][0].get_row()}"

        for key in ROW_CLS_INDEXED:
            iface = self.get(key, EMPTY_INTERFACE)
            conns = self.get(key + "c", EMPTY_CONNECTIONS)
            iface.consistency()
            conns.consistency()
            assert len(iface) == len(conns), f"Length mismatch: {len(iface)} != {len(conns)}"

            # Check desintation connections
            if key[1] == EPClsPostfix.DST:
                for idx, refs in enumerate(conns):
                    assert len(refs) == 1, f"Dst EPs must have one reference: {len(refs)}"
                    srow = refs[0].get_row()
                    assert srow in VALID_ROW_SOURCES[has_f], f"Invalid src row: {srow}"
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
                        assert drow in VALID_ROW_DESTINATIONS[has_f], f"Invalid dst row: {drow}"
                        dtyp = self[drow + EPClsPostfix.DST][ref.get_idx()]
                        assert iface[idx] == dtyp, f"Src typ mismatch: {iface[idx]} != {dtyp}"
                        drefs = self[drow + EPClsPostfix.DST + "c"][ref.get_idx()]
                        assert (
                            SrcEndPointRef(cast(Row, key[0]), idx) in drefs
                        ), f"Dst not connected to src: {key[0]}[{idx}]"
        super().consistency()

    def epkeys(self: GCGraphProtocol) -> Generator[str, None, None]:
        """Return an iterator over the GC graph endpoint keys."""
        for key in self.ikeys():
            for idx in range(len(self[key])):
                yield f"{key[0]}{idx:03d}{key[1]}"

    def get(self: GCGraphProtocol, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key."""
        try:
            return self[key]
        except KeyError:
            return default

    def ikeys(self: GCGraphProtocol) -> Generator[str, None, None]:
        """Return an iterator over the GC graph interface keys."""
        for key in (r for r in ROW_CLS_INDEXED if r in self):
            yield key

    def itypes(self: GCGraphProtocol) -> tuple[list[EndPointType], list[int]]:
        """Return the input types and input row indices into them."""
        ikey = SourceRow.I + EPClsPostfix.SRC
        itypes = list(self.types(ikey))
        ilu = {t: i for i, t in enumerate(itypes)}
        return itypes, [ilu[i] for i in self.get(ikey, EMPTY_INTERFACE)]

    def otypes(self: GCGraphProtocol) -> tuple[list[EndPointType], list[int]]:
        """Return the output types and output row indices into them."""
        okey = DestinationRow.O + EPClsPostfix.DST
        otypes = list(self.types(okey))
        olu = {t: o for o, t in enumerate(otypes)}
        return otypes, [olu[i] for i in self.get(okey, EMPTY_INTERFACE)]

    def setdefault(self: GCGraphProtocol, key: str, default: Any) -> Any:
        """Set the endpoint with the given key to the default if it does not exist."""
        if key not in self:
            self[key] = default
        return self[key]

    def to_json(self: GCGraphProtocol) -> dict[str, Any]:
        """Return a JSON GC Graph."""
        jgcg: dict[str, list[list[Any]]] = {}
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.DST and k in self):
            iface: InterfaceABC = self[key]
            conns: ConnectionsABC = self[key + "c"]
            jgcg[key[0]] = [[str(r[0].get_row()), r[0].get_idx(), t] for r, t in zip(conns, iface)]
        ucn: list[list[Any]] = []
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.SRC and k in self):
            iface: InterfaceABC = self[key]
            conns: ConnectionsABC = self[key + "c"]
            row = cast(Row, key[0])
            ucn.extend([[row, i, t] for i, (r, t) in enumerate(zip(conns, iface)) if not r])
        if ucn:
            jgcg["U"] = sorted(ucn, key=lambda x: x[0] + f"{x[1]:03d}")
        return jgcg

    def types(self: GCGraphProtocol, ikey: str) -> Generator[EndPointType, None, None]:
        """Return an iterator over the ordered interface endpoint types.
        Endpoint types are returned in the order of lowest value to highest.
        """
        return (typ for typ in sorted({typ for typ in self.get(ikey, EMPTY_INTERFACE)}))

    def verify(self: GCGraphProtocol) -> None:
        """Verify the GC graph."""
        for key in ROW_CLS_INDEXED:
            self.get(key, EMPTY_INTERFACE).verify()
        super().verify()
