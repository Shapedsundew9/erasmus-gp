"""Base class for GC graph objects."""
from __future__ import annotations
from typing import Any, Generator, Protocol
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.end_point.end_point import EndPoint
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.interface.interface_class_factory import EMPTY_INTERFACE
from egppy.gc_graph.connections.connections_class_factory import EMPTY_CONNECTIONS
from egppy.gc_graph.ep_type import ep_type_lookup
from egppy.storage.cache.cacheable_obj import CacheableObjMixin
from egppy.gc_graph.egp_typing import (SourceRow,
    EPClsPostfix, VALID_ROW_SOURCES, VALID_ROW_DESTINATIONS, ROW_CLS_INDEXED)


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCGraphProtocol(Protocol):
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

    def consistency(self) -> None:
        """Check the consistency of the GC graph."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key."""
        ...  # pylint: disable=unnecessary-ellipsis

    def to_json(self) -> dict[str, Any]:
        """Return a JSON GC Graph."""
        ...  # pylint: disable=unnecessary-ellipsis

    def verify(self) -> None:
        """Verify the GC graph."""


class GCGraphMixin(CacheableObjMixin):
    """Base class for GC graph objects."""

    def __init__(self: GCGraphProtocol, json_gc_graph: dict[str, list[list[Any]]]) -> None:
        """Initialize the GC graph."""
        if _LOG_VERIFY:
            self.verify()
        if _LOG_CONSISTENCY:
            self.consistency()
            assert self.to_json() == json_gc_graph, "JSON GC Graph consistency failure."
        super().__init__()

    def __contains__(self: GCGraphProtocol, key: object) -> bool:
        """Return True if the row, interface or endpoint exists."""
        if isinstance(key, str):
            keylen = len(key)
            if keylen == 1:  # Its a row
                return self.get(key + 'd', EMPTY_INTERFACE) is not EMPTY_INTERFACE or \
                    self.get(key + 's', EMPTY_INTERFACE) is not EMPTY_INTERFACE
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
        for key in ROW_CLS_INDEXED:
            for idx in range(len(self[key])):
                yield self[f"{key[0]}{idx:03d}{key[1]}"]

    def conditional_graph(self: GCGraphProtocol) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return 'F' in self

    def consistency(self: GCGraphProtocol) -> None:
        """Check the consistency of the GC graph."""
        has_f = self.conditional_graph()
        # Check graph structure
        if has_f:
            fi: InterfaceABC = self['F' + EPClsPostfix.DST]
            assert len(fi) == 1, f"Row F must only have one end point: {len(fi)}"
            assert fi[0] == ep_type_lookup['n2v']['bool'], f"F EP must be bool: {fi[0]}"
            fc: ConnectionsABC = self['F' + EPClsPostfix.DST + 'c']
            assert len(fc) == 1, f"Row F must only have one connection: {len(fc)}"
            assert fc[0][0].get_row() == SourceRow.I, f"Row F src must be I: {fc[0][0].get_row()}"

        for key in ROW_CLS_INDEXED:
            iface = self[key]
            conns = self[key + 'c']
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
                    srefs = self[srow + EPClsPostfix.SRC + 'c'][refs[0].get_idx()]
                    assert (key[0], idx) in srefs, f"Src not connected to Dst: {key[0]}[{idx}]"
            else:
                # Check source connections
                for idx, refs in enumerate(conns):
                    for ref in refs:
                        drow = ref.get_row()
                        assert drow in VALID_ROW_DESTINATIONS[has_f], f"Invalid dst row: {drow}"
                        dtyp = self[drow + EPClsPostfix.DST][ref.get_idx()]
                        assert iface[idx] == dtyp, f"Src typ mismatch: {iface[idx]} != {dtyp}"
                        drefs = self[drow + EPClsPostfix.DST + 'c'][ref.get_idx()]
                        assert (key[0], idx) in drefs, f"Dst not connected to src: {key[0]}[{idx}]"

    def get(self: GCGraphProtocol, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key."""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self: GCGraphProtocol, key: str, default: Any) -> Any:
        """Set the endpoint with the given key to the default if it does not exist."""
        if key not in self:
            self[key] = default
        return self[key]

    def to_json(self: GCGraphProtocol) -> dict[str, Any]:
        """Return a JSON GC Graph."""
        jgcg: dict[str, list[list[Any]]] = {}
        for key in (k for k in ROW_CLS_INDEXED if k[1] == EPClsPostfix.DST):
            iface: InterfaceABC = self[key]
            conns: ConnectionsABC = self[key + 'c']
            jgcg[key[0]] = [[r[0].get_row(), r[0].get_idx(), i] for r, i in zip(conns, iface)]
        return jgcg

    def verify(self: GCGraphProtocol) -> None:
        """Verify the GC graph."""
        for key in ROW_CLS_INDEXED:
            self[key].verify()
            self[key].verify()
