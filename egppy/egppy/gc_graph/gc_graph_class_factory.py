"""Builtin graph classes for the GC graph."""
from __future__ import annotations
from typing import Any, Iterable, cast
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.end_point.end_point import EndPoint, SrcEndPointRef
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.interface.interface_class_factory import TupleInterface, EMPTY_INTERFACE
from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_class_factory import TupleConnections, EMPTY_CONNECTIONS
from egppy.gc_graph.egp_typing import (EndPointClass, Row, SourceRow, EndPointType, ROW_CLS_INDEXED,
    CPI, SOURCE_ROWS, str2epcls)
from egppy.gc_graph.gc_graph_mixin import GCGraphMixin, GCGraphProtocol
from egppy.gc_graph.gc_graph_abc import GCGraphABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Empty GC Graph templates
_EMPTY_INTERFACES: dict[str, InterfaceABC] = {r: EMPTY_INTERFACE for r in ROW_CLS_INDEXED}
_EMPTY_CONNECTIONS: dict[str, ConnectionsABC] = {r: EMPTY_CONNECTIONS for r in ROW_CLS_INDEXED}


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


class StaticGCGraph(GCGraphMixin, GCGraphProtocol, GCGraphABC):
    """Builtin graph class for the GC graph."""

    def __init__(self, json_gc_graph: dict[str, list[list[Any]]]) -> None:
        """Initialize the GC graph.
        Construct the internal representation of the graph from the JSON graph.
        """
        self._interfaces: dict[str, InterfaceABC] = _EMPTY_INTERFACES.copy()
        self._connections: dict[str, ConnectionsABC] = _EMPTY_CONNECTIONS.copy()
        self._dirty_rows: set[str] = set()
        src_interface_typs: dict[SourceRow, set[tuple]] = {r: set() for r in SOURCE_ROWS}
        src_interface_refs: dict[SourceRow, dict[int, list[tuple]]] = {r: {} for r in SOURCE_ROWS}

        # Step through the json_gc_graph and create the interfaces and connections
        for idx, (row, jeps) in enumerate(json_gc_graph.items()):
            # Row U only exists in the JSON GC Graph to identify unconnected src endpoints
            # Otherwise it is a valid destination row
            if row != "U":
                rowd = row + 'd'
                self._set_interface(rowd, TupleInterface([jep[CPI.TYP] for jep in jeps]))
                self._set_connections(rowd, TupleConnections(
                    ((jep[CPI.ROW], jep[CPI.IDX]) for jep in jeps)))
                # Convert each dst endpoint into a dst reference for a src endpoint
                for jep in jeps:
                    src_interface_refs[jep[CPI.ROW]].setdefault(jep[CPI.IDX],[]).append((row, idx))
            # Collect the references to the source interfaces - this is used to define them below
            for jep in jeps:
                src_interface_typs[jep[CPI.ROW]].add((jep[CPI.IDX], jep[CPI.TYP]))

        # Create the source interfaces from the references collected above
        for row, sif in src_interface_typs.items():
            self._set_interface(row + 's', TupleInterface((t for _, t in sorted(sif, key=skey))))
        # Add the references to the destinations from the sources
        for row, idx_refs in src_interface_refs.items():
            src_refs = [tuple()] * len(self._interfaces[row + 's'])
            for idx, refs in idx_refs.items():
                src_refs[idx] = tuple(SrcEndPointRef(r[0], r[1]) for r in refs)
            self._set_connections(row + 's', TupleConnections(src_refs))

        # Call the mixin constructor & run the sanity checks
        super().__init__(json_gc_graph)

    def __delitem__(self, key: str) -> None:
        """Cannot modify a static graph."""
        raise RuntimeError("Cannot modify a static graph.")

    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        self.touch()
        if isinstance(key, str):
            keylen = len(key)
            if keylen == 2:  # Its an interface
                iface = self._interfaces.get(key, EMPTY_INTERFACE)
                if iface is EMPTY_INTERFACE:
                    raise KeyError(f"Interface {key} does not exist.")
                return iface
            if keylen == 3:  # Its connections
                conns = self._connections.get(key[:2], EMPTY_CONNECTIONS)
                if conns is EMPTY_CONNECTIONS:
                    raise KeyError(f"Connections {key} does not exist.")
                return conns
            if keylen == 5:  # Its an endpoint
                iface = self._interfaces.get(key[0] + key[4], EMPTY_INTERFACE)
                if iface is EMPTY_INTERFACE:
                    raise KeyError(f"Endpoint {key} does not exist.")
                conns = self._connections.get(key[0] + key[4] + 'c', EMPTY_CONNECTIONS)
                assert conns is not EMPTY_CONNECTIONS, \
                    f"Connections {key} does not exist when interface does."
                k, i, c = key2parts(key)
                return EndPoint(k, i, iface[i], c, conns[i])
        raise KeyError(f"Invalid GC Graph key: {key}")

    def __len__(self) -> int:
        """Return the total number of endpoints."""
        return sum(len(self._interfaces[key]) for key in ROW_CLS_INDEXED)

    def __setitem__(self, key: str, value: Any) -> None:
        """Cannot modify a static graph."""
        raise RuntimeError("Cannot modify a static graph.")

    def _set_connections(self, key: str,
        conns: ConnectionsABC | Iterable[Iterable[XEndPointRefABC]]) -> None:
        """Set the connections object for the given key."""
        self.dirty()
        self._dirty_rows.add(key)
        if isinstance(conns, ConnectionsABC):
            self._connections[key] = conns
        else:
            self._connections[key] = TupleConnections(conns)

    def _set_interface(self, key: str, iface: InterfaceABC | Iterable[EndPointType]) -> None:
        """Set the interface object for the given key."""
        self.dirty()
        self._dirty_rows.add(key)
        if isinstance(iface, InterfaceABC):
            self._interfaces[key] = iface
        else:
            self._interfaces[key] = TupleInterface(iface)

    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return self._interfaces['Fd'] is not EMPTY_INTERFACE

    def modified(self) -> tuple[str | int, ...] | bool:
        """Return the modification status of the GC Graph."""
        # Static graphs are never modified
        return False
