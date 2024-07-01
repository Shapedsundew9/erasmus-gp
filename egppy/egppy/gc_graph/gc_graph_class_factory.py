"""Builtin graph classes for the GC graph."""
from __future__ import annotations
from typing import Any, Iterable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.end_point.builtin_end_point import BuiltinSrcEndPointRef
from egppy.gc_graph.end_point.end_point_abc import XEndPointRefABC
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.interface.interface_class_factory import TupleInterface, EMPTY_INTERFACE
from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_class_factory import TupleConnections, EMPTY_CONNECTIONS
from egppy.gc_graph.egp_typing import SourceRow, EndPointType, ROW_CLS_INDEXED, CPI, SOURCE_ROWS
from egppy.gc_graph.gc_graph_mixin import GCGraphMixin
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


class BuiltinGCGraph(GCGraphMixin, GCGraphABC):
    """Builtin graph class for the GC graph."""

    def __init__(self, json_gc_graph: dict[str, list[list[Any]]]) -> None:
        """Initialize the GC graph.
        Construct the internal representation of the graph from the JSON graph.
        """
        self.interfaces: dict[str, InterfaceABC] = _EMPTY_INTERFACES.copy()
        self.connections: dict[str, ConnectionsABC] = _EMPTY_CONNECTIONS.copy()
        self._dirty = True
        src_interface_typs: dict[SourceRow, set[tuple]] = {r: set() for r in SOURCE_ROWS}
        src_interface_refs: dict[SourceRow, dict[int, list[tuple]]] = {r: {} for r in SOURCE_ROWS}

        # Step through the json_gc_graph and create the interfaces and connections
        for idx, (row, jeps) in enumerate(json_gc_graph.items()):
            # Row U only exists in the JSON GC Graph to identify unconnected src endpoints
            # Otherwise it is a valid destination row
            if row != "U":
                rowd = row + 'd'
                self.interfaces[rowd] = TupleInterface([jep[CPI.TYP] for jep in jeps])
                self.connections[rowd] = TupleConnections(
                    ((jep[CPI.ROW], jep[CPI.IDX]) for jep in jeps))
                # Convert each dst endpoint into a dst reference for a src endpoint
                for jep in jeps:
                    src_interface_refs[jep[CPI.ROW]].setdefault(jep[CPI.IDX],[]).append((row, idx))
            # Collect the references to the source interfaces - this is used to define them below
            for jep in jeps:
                src_interface_typs[jep[CPI.ROW]].add((jep[CPI.IDX], jep[CPI.TYP]))

        # Create the source interfaces from the references collected above
        for row, sif in src_interface_typs.items():
            self.interfaces[row + 's'] = TupleInterface((t for _, t in sorted(sif, key=skey)))
        # Add the references to the destinations from the sources
        for row, idx_refs in src_interface_refs.items():
            src_refs = [tuple()] * len(self.interfaces[row + 's'])
            for idx, refs in idx_refs.items():
                src_refs[idx] = tuple(BuiltinSrcEndPointRef(r[0], r[1]) for r in refs)
            self.connections[row + 's'] = TupleConnections(src_refs)

        # Run the mixin initialization (sanity checks, cacheable setup etc.)
        super().__init__(json_gc_graph)

    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return 'Fd' in self.interfaces

    def get_connections(self, key: str) -> ConnectionsABC:
        """Return the connections object for the given key."""
        self.touch()
        return self.connections[key]

    def get_interface(self, key: str) -> InterfaceABC:
        """Return the interface object for the given key."""
        self.touch()
        return self.interfaces[key]

    def set_connections(self, key: str,
        conns: ConnectionsABC | Iterable[Iterable[XEndPointRefABC]]) -> None:
        """Set the connections object for the given key."""
        self.dirty()
        if isinstance(conns, ConnectionsABC):
            self.connections[key] = conns
        else:
            self.connections[key] = TupleConnections(conns)

    def set_interface(self, key: str, iface: InterfaceABC | Iterable[EndPointType]) -> None:
        """Set the interface object for the given key."""
        self.dirty()
        if isinstance(iface, InterfaceABC):
            self.interfaces[key] = iface
        else:
            self.interfaces[key] = TupleInterface(iface)
