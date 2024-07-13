"""Base class for GC graph objects."""
from __future__ import annotations
from typing import Any, cast, Iterable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.end_point.end_point_abc import EndPointABC, XEndPointRefABC
from egppy.gc_graph.end_point.builtin_end_point import BuiltinEndPoint
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.ep_type import ep_type_lookup
from egppy.storage.cache.cacheable_obj import CacheableObjMixin
from egppy.gc_graph.egp_typing import (SourceRow, ep_cls_str_to_ep_cls_int, Row, ROWS, EndPointType,
    EPClsPostfix, VALID_ROW_SOURCES, VALID_ROW_DESTINATIONS, ROW_CLS_INDEXED)


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCGraphMixin(CacheableObjMixin):
    """Base class for GC graph objects."""

    def __init__(self, json_gc_graph: dict[str, list[list[Any]]]) -> None:
        """Initialize the GC graph."""
        if _LOG_VERIFY:
            self.verify()
        if _LOG_CONSISTENCY:
            self.consistency()
            assert self.to_json() == json_gc_graph, "JSON GC Graph consistency failure."
        super().__init__()

    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        raise NotImplementedError("GCGraphMixin.conditional_graph must be overridden")

    def consistency(self) -> None:
        """Check the consistency of the GC graph."""
        has_f = self.conditional_graph()
        # Check graph structure
        if has_f:
            fi: InterfaceABC = self.get_interface('F' + EPClsPostfix.DST)
            assert len(fi) == 1, f"Row F must only have one end point: {len(fi)}"
            assert fi[0] == ep_type_lookup['n2v']['bool'], f"F EP must be bool: {fi[0]}"
            fc: ConnectionsABC = self.get_connections('F' + EPClsPostfix.DST)
            assert len(fc) == 1, f"Row F must only have one connection: {len(fc)}"
            assert fc[0][0].get_row() == SourceRow.I, f"Row F src must be I: {fc[0][0].get_row()}"

        for key in ROW_CLS_INDEXED:
            iface = self.get_interface(key)
            conns = self.get_connections(key)
            iface.consistency()
            conns.consistency()
            assert len(iface) == len(conns), f"Length mismatch: {len(iface)} != {len(conns)}"

            # Check desintation connections
            if key[1] == EPClsPostfix.DST:
                for idx, refs in enumerate(conns):
                    assert len(refs) == 1, f"Dst EPs must have one reference: {len(refs)}"
                    srow = refs[0].get_row()
                    assert srow in VALID_ROW_SOURCES[has_f], f"Invalid src row: {srow}"
                    styp = self.get_interface(srow + EPClsPostfix.SRC)[refs[0].get_idx()]
                    assert iface[idx] == styp, f"Dst EP type mismatch: {iface[idx]} != {styp}"
                    srefs = self.get_connections(srow + EPClsPostfix.SRC)[refs[0].get_idx()]
                    assert (key[0], idx) in srefs, f"Src not connected to Dst: {key[0]}[{idx}]"
            else:
                # Check source connections
                for idx, refs in enumerate(conns):
                    for ref in refs:
                        drow = ref.get_row()
                        assert drow in VALID_ROW_DESTINATIONS[has_f], f"Invalid dst row: {drow}"
                        dtyp = self.get_interface(drow + EPClsPostfix.DST)[ref.get_idx()]
                        assert iface[idx] == dtyp, f"Src typ mismatch: {iface[idx]} != {dtyp}"
                        drefs = self.get_connections(drow + EPClsPostfix.DST)[ref.get_idx()]
                        assert (key[0], idx) in drefs, f"Dst not connected to src: {key[0]}[{idx}]"

    def get_connections(self, key: str) -> ConnectionsABC:
        """Return the connections object for the given key."""
        raise NotImplementedError("GCGraphMixin.get_connections must be overridden")

    def get_endpoints(self, key: str) -> list[EndPointABC]:
        """Return the endpoints for a given interface.
        NOTE: Modification of the endpoints does not modify the graph.
        To modify the graph use the set_endpoints() method.

        Args:
            key: The interface/connections key i.e. "[row][s|d]".
        """
        if _LOG_VERIFY:
            assert key[0] in ROWS, f"Invalid row: {key[0]}"
            assert key[1] in ['s', 'd'], f"Invalid endpoint class: {key[1]}"

        row = cast(Row, key[0])
        cls = ep_cls_str_to_ep_cls_int(key[1])
        iface = self.get_interface(key)
        conns = self.get_connections(key)
        return [BuiltinEndPoint(row=row, idx=idx, typ=iface[idx], cls=cls,
            refs=conns[idx]) for idx in range(len(conns))]

    def get_interface(self, key: str) -> InterfaceABC:
        """Return the interface object for the given key."""
        raise NotImplementedError("GCGraphMixin.get_interface must be overridden")

    def set_connections(self, key: str,
            conns: ConnectionsABC | Iterable[Iterable[XEndPointRefABC]]) -> None:
        """Set the connections for a given interface.

        Args:
            key: The interface/connections key i.e. "[row][s|d]".
            conns: The connections object.
        """
        raise NotImplementedError("GCGraphMixin.set_connections must be overridden")

    def set_endpoints(self, key: str, endpoints: Iterable[EndPointABC]) -> None:
        """Set the endpoints for a given interface."""
        if _LOG_VERIFY:
            assert key[0] in ROWS, f"Invalid row: {key[0]}"
            assert key[1] in ['s', 'd'], f"Invalid endpoint class: {key[1]}"

        self.set_connections(key, [ep.get_refs() for ep in endpoints])
        self.set_interface(key, [ep.get_typ() for ep in endpoints])

    def set_interface(self, key: str, iface: InterfaceABC | Iterable[EndPointType]) -> None:
        """Set the interface for the given key."""
        raise NotImplementedError("GCGraphMixin.set_interface must be overridden")

    def to_json(self) -> dict[str, Any]:
        """Return a JSON GC Graph."""
        jgcg: dict[str, list[list[Any]]] = {}
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.DST):
            iface: InterfaceABC = self.get_interface(key)
            conns: ConnectionsABC = self.get_connections(key)
            jgcg[key[0]] = [[r[0].get_row(), r[0].get_idx(), i] for r, i in zip(conns, iface)]
        return jgcg

    def verify(self) -> None:
        """Verify the GC graph."""
        for key in ROW_CLS_INDEXED:
            self.get_interface(key).verify()
            self.get_connections(key).verify()
